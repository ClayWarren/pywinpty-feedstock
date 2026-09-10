#include <stdio.h>
#include <wchar.h>
#include <winpty.h>

int main(void)
{
    winpty_error_ptr_t error = NULL;
    winpty_config_t *config = winpty_config_new(0, &error);
    winpty_t *pty;
    int result;
    if (config == NULL) {
        fwprintf(stderr, L"config: %ls\n", winpty_error_msg(error));
        winpty_error_free(error);
        return 1;
    }
    winpty_config_set_initial_size(config, 80, 25);
    pty = winpty_open(config, &error);
    winpty_config_free(config);
    if (pty == NULL) {
        fwprintf(stderr, L"open: %ls\n", winpty_error_msg(error));
        winpty_error_free(error);
        return 1;
    }
    result = winpty_set_size(pty, 100, 30, &error);
    if (!result) {
        fwprintf(stderr, L"resize: %ls\n", winpty_error_msg(error));
        winpty_error_free(error);
    }
    winpty_free(pty);
    return result ? 0 : 1;
}
