"""Exercise both installed PTY backends, including child-observed resize."""
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import sysconfig
import time


def exercise(backend_name):
    if backend_name == 'ConPTY':
        os.environ['CI'] = '1'
        os.environ['CONPTY_CI'] = '1'
    else:
        os.environ.pop('CI', None)
        os.environ.pop('CONPTY_CI', None)
    from winpty import PTY
    from winpty.enums import Backend

    if sysconfig.get_config_var('Py_GIL_DISABLED'):
        assert not sys._is_gil_enabled(), 'Import unexpectedly enabled the GIL'
    child = (
        "import os,sys; "
        "print('PTY_READY',flush=True); "
        "text=input(); "
        "print('RECEIVED:'+text[::-1],flush=True); "
        "input(); "
        "size=os.get_terminal_size(); "
        "print('SIZE:%d:%d'%(size.columns,size.lines),flush=True); "
        "input()"
    )
    pty = PTY(80, 25, backend=getattr(Backend, backend_name))
    assert pty.spawn(sys.executable, subprocess.list2cmdline([sys.executable, '-u', '-c', child]))
    output = ''

    def expect(text):
        nonlocal output
        deadline = time.monotonic() + 20
        while text not in output and time.monotonic() < deadline:
            output += pty.read(blocking=False)
            time.sleep(0.05)
        assert text in output, (text, output)
        output = ''

    expect('PTY_READY')
    payload = 'terminal ünicode'
    assert pty.write(payload + '\r\n') > 0
    expect('RECEIVED:' + payload[::-1])
    pty.set_size(101, 37)
    pty.write('resize\r\n')
    expect('SIZE:101:37')
    pty.write('exit\r\n')
    deadline = time.monotonic() + 20
    while pty.isalive() and time.monotonic() < deadline:
        pty.read(blocking=False)
        time.sleep(0.05)
    assert not pty.isalive(), 'Child failed to exit'
    print('PASS:', backend_name, 'Unicode I/O, child-observed resize, exit')


if __name__ == '__main__':
    if len(sys.argv) == 2:
        exercise(sys.argv[1])
    else:
        import winpty
        machine = platform.machine().lower()
        expected = 0xAA64 if machine in ('arm64', 'aarch64') else 0x8664
        package_dir = Path(winpty.__file__).parent
        binaries = [Path(sys.executable), *package_dir.glob('*.pyd'),
                    package_dir / 'conpty.dll', package_dir / 'OpenConsole.exe',
                    Path(sys.prefix) / 'Library/bin/winpty.dll',
                    Path(sys.prefix) / 'Library/bin/winpty-agent.exe']
        assert list(package_dir.glob('*.pyd')), 'Missing extension module'
        for binary in binaries:
            data = binary.read_bytes()
            offset = struct.unpack_from('<I', data, 60)[0]
            assert data[offset:offset + 4] == b'PE\0\0', binary
            actual = struct.unpack_from('<H', data, offset + 4)[0]
            assert actual == expected, (binary, hex(actual), hex(expected))
            print('Verified PE architecture:', binary.name, hex(actual), flush=True)
        for backend in ('ConPTY', 'WinPTY'):
            subprocess.run([sys.executable, __file__, backend], check=True, timeout=90)
