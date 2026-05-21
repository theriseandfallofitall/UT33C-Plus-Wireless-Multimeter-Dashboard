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
    expected=(frame[0]+frame[1]+frame[2]+frame[3]+frame[4]+frame[8]+frame[9]) & 0xFF
    return frame[5]==expected

def decode_frame(frame:bytes)->Optional[DecodedFrame]:
    if len(frame)!=10 or frame[6]!=0xAB or frame[7]!=0xCD or not checksum_ok(frame):
        return None
    mode, range_id = frame[8], frame[9]
    raw=signed16((frame[2]<<8)|frame[3])
    if mode==0x01 and range_id==0x0D:
        return DecodedFrame(frame, raw, raw/100.0, 'V', mode, range_id)
    if mode==0x01 and range_id==0x15:
        return DecodedFrame(frame, raw, raw/10.0, 'V', mode, range_id)
    return DecodedFrame(frame, raw, float(raw), 'raw', mode, range_id)

def frame_to_hex(frame:bytes)->str:
    return ' '.join(f'{b:02X}' for b in frame)

def find_frames(buffer:bytearray)->list[bytes]:
    frames=[]
    while len(buffer)>=10:
        found=False
        for marker in range(len(buffer)-1):
            if buffer[marker]==0xAB and buffer[marker+1]==0xCD:
                start=marker-6
                if start<0:
                    if marker>0: del buffer[:marker]
                    return frames
                if len(buffer)<start+10: return frames
                candidate=bytes(buffer[start:start+10])
                del buffer[:start+10]
                found=True
                if checksum_ok(candidate): frames.append(candidate)
                break
        if not found:
            del buffer[:-1]
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
