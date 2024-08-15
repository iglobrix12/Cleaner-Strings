Для настройки чистильщика Process Hacker 2 и System Informer установите необходимые библиотеки.

Для настройки очистки:

```
search_strings = ["exloader", "Exloader", "ExLoader", "ENIGMA", "enigma", "swiss", "en1gma", "cheat", "Download", "C:/", "/C:/", "XONE", "xone", "AXIOMA", "axioma", "midnight", "MIDNI", "soft"]
search_and_replace_in_process("explorer.exe", search_strings)
```
В процессе ```explorer.exe``` будут очищены ```Strings```, указанные в массиве search_strings. Эти строки будут удалены.
