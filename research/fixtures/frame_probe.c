/* Original FL Commons research fixture, MIT licensed. No FL Studio code. */
__declspec(dllexport) int fc_is_frame(const unsigned char *data, unsigned int size)
{
    if (size < 7 || size > 4096)
        return 0;
    return data[0] == 0xf0 && data[1] == 0x7d && data[2] == 0x46 &&
           data[3] == 0x43 && data[4] == 1 && data[size - 1] == 0xf7;
}

__declspec(dllexport) unsigned int fc_next_sequence(unsigned int current)
{
    return current == 0xffffffffU ? 0 : current + 1;
}
