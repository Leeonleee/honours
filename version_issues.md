# Version Issues

This file is for documenting all the versioning issues that occur

## All dependencies

All the things that need to be downloaded for compilation to work

- `cmake 3.31.7`

## CMake

- Older version requires `cmake_minimum_required(VERSION 2.8.12)`, but CMake 4.0.1 doesn't support versions below 3.5 anymore

### Fix

- Downloaded cmake version 3.31.7

```
export PATH=/opt/cmake-3.31.7-linux-x86_64/bin:$PATH
```

- This sets cmake to version 3.31.7 for the current terminal session

## GCC

- The `<cstdint.h>` include error happens in multiple files
- Older versions require older GCC/G++ versions. GCC 14+ is too new
- I tried including `<cstdint.h>` but it didn't work, but `<stdint.h>` worked. I googled and apparently it used to be called that?

### Fix (Not working yet)

- Downloaded GCC 12.1

```
export CC=/usr/bin/gcc-12
export CXX=/usr/bin/g++-12
```