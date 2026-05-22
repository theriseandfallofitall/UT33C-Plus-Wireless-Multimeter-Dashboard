#!/usr/bin/env python3
"""UNI-T UT33C+ UART logger / decoder.

Install: pip install pyserial
Usage:
  python ut33c_plus_logger.py --port COM5
  python ut33c_plus_logger.py --port /dev/ttyUSB0 --csv readings.csv
"""
from __future__ import annotations
import argparse, csv, sys, time
from dataclasses import dataclass
from typing import Optional
try:
    import serial
except ImportError:
    print('Missing dependency: pyserial. Install with: pip install pyserial', file=sys.stderr)
    raise

@dataclass
class DecodedFrame:
    raw_frame: bytes
    raw_count: int
    value: float
    unit: str
    mode: int
    range_id: int

def signed16(value:int)->int:
    return value-0x10000 if value & 0x8000 else value

def checksum_ok(frame:bytes)->bool:
    if len(frame)!=10: return False
    # CS = (MODE + RANGE + B0 + B1 + B2 + B3 + B4) & 0xFF
    # Bytes are: AB CD MODE RANGE B0 B1 B2 B3 B4 CS
    #            0  1  2    3     4  5  6  7  8  9
    expected=sum(frame[2:9]) & 0xFF
    return frame[9]==expected

def decode_frame(frame:bytes)->Optional[DecodedFrame]:
    if len(frame)!=10 or frame[0]!=0xAB or frame[1]!=0xCD or not checksum_ok(frame):
        return None
    mode, range_id = frame[2], frame[3]
    raw=signed16((frame[6]<<8)|frame[7])
    
    if mode==0x01:
        if range_id==0x17: return DecodedFrame(frame, raw, raw/10.0, 'mV', mode, range_id)
        if range_id==0x0D: return DecodedFrame(frame, raw, raw/100.0, 'V', mode, range_id)
        if range_id==0x15: return DecodedFrame(frame, raw, raw/10.0, 'V', mode, range_id)
        if range_id==0x1E: return DecodedFrame(frame, raw, float(raw), 'Ohm', mode, range_id)
        if range_id==0x0E: return DecodedFrame(frame, raw, raw/100.0, 'kOhm', mode, range_id)
        if range_id==0x1A: return DecodedFrame(frame, raw, raw/10.0, 'kOhm', mode, range_id)
        if range_id==0x1C: return DecodedFrame(frame, raw, raw/10.0, 'M0hm (High)', mode, range_id)
        if range_id==0x16: return DecodedFrame(frame, raw, raw/10.0, 'degC', mode, range_id)
        if range_id==0x13: return DecodedFrame(frame, raw, raw/10.0, 'degF', mode, range_id)
        if range_id==0x0B: return DecodedFrame(frame, raw, raw/100.0, 'A', mode, range_id)
        if range_id==0x1F: 
            val = "OVERLOAD" if raw == 121 else str(raw)
            return DecodedFrame(frame, raw, float(raw), 'uA' if raw != 121 else val, mode, range_id)
        if range_id==0x1B:
            val = "OVERLOAD" if raw == 121 else str(raw/100.0)
            return DecodedFrame(frame, raw, raw/100.0, 'mA' if raw != 121 else val, mode, range_id)
        if range_id==0x0F:
            val = "OVERLOAD" if raw == 121 else str(raw/10.0)
            return DecodedFrame(frame, raw, raw/10.0, 'mA' if raw != 121 else val, mode, range_id)
        if range_id==0x19:
            # Both Diode and Continuity use 0x19
            # Heuristic: 0x7F00 (32512) is "Open" in continuity, 0 is "Short".
            # Small values in this range are usually Diode drops (e.g., 608 for 0.608V).
            if raw == 0x7F00:
                return DecodedFrame(frame, raw, 1.0, 'OPEN', mode, range_id)
            if raw == 0:
                return DecodedFrame(frame, raw, 0.0, 'SHORT', mode, range_id)
            if raw < 5000: # Typical diode drops < 5V
                return DecodedFrame(frame, raw, raw/1000.0, 'V (Diode)', mode, range_id)
            return DecodedFrame(frame, raw, float(raw), 'raw (0x19)', mode, range_id)
            
    return DecodedFrame(frame, raw, float(raw), 'raw', mode, range_id)

def frame_to_hex(frame:bytes)->str:
    return ' '.join(f'{b:02X}' for b in frame)

def find_frames(buffer:bytearray)->list[bytes]:
    frames=[]
    while len(buffer)>=10:
        found=False
        for i in range(len(buffer)-1):
            if buffer[i]==0xAB and buffer[i+1]==0xCD:
                if len(buffer)<i+10: return frames
                candidate=bytes(buffer[i:i+10])
                if checksum_ok(candidate):
                    frames.append(candidate)
                    del buffer[:i+10]
                    found=True
                    break
                else:
                    # Invalid checksum, skip this marker
                    continue
        if not found:
            # No valid markers in the first part, but there might be later
            # Keep enough for a partial match
            del buffer[:-1]
            break
    return frames

def main()->int:
    p=argparse.ArgumentParser(description='UNI-T UT33C+ UART logger/decoder')
    p.add_argument('--port', required=True, help='Serial port, e.g. COM5 or /dev/ttyUSB0')
    p.add_argument('--baud', type=int, default=2400)
    p.add_argument('--csv')
    p.add_argument('--raw', action='store_true', help='Also print checksum-valid unknown ranges')
    args=p.parse_args()
    csv_file=None; writer=None
    if args.csv:
        csv_file=open(args.csv,'w',newline='',encoding='utf-8')
        writer=csv.writer(csv_file)
        writer.writerow(['timestamp','frame_hex','mode','range','raw_count','value','unit'])
    buffer=bytearray()
    try:
        with serial.Serial(args.port,args.baud,bytesize=8,parity='N',stopbits=1,timeout=0.2) as ser:
            print(f'Listening on {args.port} at {args.baud} baud. Press Ctrl+C to stop.')
            while True:
                data=ser.read(64)
                if not data: continue
                buffer.extend(data)
                for frame in find_frames(buffer):
                    d=decode_frame(frame)
                    if d is None: continue
                    ts=time.strftime('%Y-%m-%d %H:%M:%S')
                    hx=frame_to_hex(frame)
                    print(f'{ts} {d.value:.3f} {d.unit} raw={d.raw_count} mode=0x{d.mode:02X} range=0x{d.range_id:02X} frame={hx}')
                    if writer:
                        writer.writerow([ts,hx,f'0x{d.mode:02X}',f'0x{d.range_id:02X}',d.raw_count,d.value,d.unit])
                        csv_file.flush()
    except KeyboardInterrupt:
        print('\nStopped.')
    finally:
        if csv_file: csv_file.close()
    return 0
if __name__=='__main__':
    raise SystemExit(main())
