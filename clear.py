import ctypes
import ctypes.wintypes as wintypes
import psutil

PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04
MEM_RELEASE = 0x8000

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD)
    ]

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
OpenProcess.restype = wintypes.HANDLE

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [
    wintypes.HANDLE,
    wintypes.LPCVOID,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t)
]
ReadProcessMemory.restype = wintypes.BOOL

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t)
]
WriteProcessMemory.restype = wintypes.BOOL

VirtualQueryEx = kernel32.VirtualQueryEx
VirtualQueryEx.argtypes = [
    wintypes.HANDLE,
    wintypes.LPCVOID,
    ctypes.POINTER(MEMORY_BASIC_INFORMATION),
    ctypes.c_size_t
]
VirtualQueryEx.restype = ctypes.c_size_t

VirtualFreeEx = kernel32.VirtualFreeEx
VirtualFreeEx.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    ctypes.c_size_t,
    wintypes.DWORD
]
VirtualFreeEx.restype = wintypes.BOOL

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]
CloseHandle.restype = wintypes.BOOL

def get_process_id_by_name(process_name):
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() == process_name.lower():
                return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def search_and_replace_in_process(process_name, search_strings, replace_string=""):
    pid = get_process_id_by_name(process_name)
    if pid is None:
        print(f"Процесс '{process_name}' не найден.")
        return

    process_handle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not process_handle:
        print(f"Не удалось открыть процесс '{process_name}'")
        return

    address = 0
    memory_info = MEMORY_BASIC_INFORMATION()

    while VirtualQueryEx(process_handle, address, ctypes.byref(memory_info), ctypes.sizeof(memory_info)):
        base_address = memory_info.BaseAddress
        region_size = memory_info.RegionSize

        buffer = ctypes.create_string_buffer(region_size)
        bytes_read = ctypes.c_size_t(0)

        if ReadProcessMemory(process_handle, base_address, buffer, region_size, ctypes.byref(bytes_read)):
            buffer_string = buffer.raw

            for search_string in search_strings:
                offset = buffer_string.find(search_string.encode())
                if offset != -1:
                    print(f"процесс '{search_string}' удалён")
                    new_buffer = (buffer_string[:offset] + replace_string.encode() + buffer_string[offset+len(search_string):])
                    bytes_written = ctypes.c_size_t(0)
                    WriteProcessMemory(process_handle, base_address, new_buffer, len(new_buffer), ctypes.byref(bytes_written))

                    if VirtualFreeEx(process_handle, base_address, region_size, MEM_RELEASE):
                        print(f"")

        address += region_size

    CloseHandle(process_handle)
    print("всё")

if __name__ == "__main__":
    search_strings = ["exloader", "Exloader", "ExLoader", "ENIGMA", "enigma", "swiss", "en1gma", "cheat", "Download", "C:/", "/C:/", "XONE", "xone", "AXIOMA", "axioma", "midnight", "MIDNI", "soft"]
    search_and_replace_in_process("explorer.exe", search_strings)
