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
    from winpty import PTY, WinptyError
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
    # Match PtyProcess.spawn: arguments only, with a leading space for WinPTY.
    cmdline = ' ' + subprocess.list2cmdline(['-u', '-c', child])
    assert pty.spawn(sys.executable, cmdline)
    output = ''

    def expect(text):
        nonlocal output
        deadline = time.monotonic() + 20
        while text not in output and time.monotonic() < deadline:
            try:
                output += pty.read(blocking=False)
            except WinptyError as error:
                raise AssertionError((backend_name, text, output, pty.get_exitstatus())) from error
            time.sleep(0.05)
        assert text in output, (text, output)
        output = ''

    expect('PTY_READY')
    payload = 'terminal ünicode'
    # ConPTY can return zero while an asynchronous write is pending.
    pty.write(payload + '\r\n')
    expect('RECEIVED:' + payload[::-1])
    pty.set_size(101, 37)
    pty.write('resize\r\n')
    expect('SIZE:101:37')
    pty.write('exit\r\n')
    deadline = time.monotonic() + 20
    while pty.isalive() and time.monotonic() < deadline:
        time.sleep(0.05)
    assert not pty.isalive(), 'Child failed to exit'
    assert pty.get_exitstatus() == 0, pty.get_exitstatus()
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
