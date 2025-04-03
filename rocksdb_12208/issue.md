# Issue 12208

## Description
I used DeleteFilesInRange to delete all the SST files in the integrated BlobDB,
and while all the SST files were successfully reclaimed, the blob files were not.

Rocksdb version: both v8.3.3 and the current main branch.

Expected behavior
All blob files should be reclaimed.

Actual behavior
The output of db->GetProperty("rocksdb.sstables", &v) shows that the SST files are empty, but the blob files are not empty.
```
--- level 0 --- version# 15 ---
--- level 1 --- version# 15 ---
--- level 2 --- version# 15 ---
--- level 3 --- version# 15 ---
--- level 4 --- version# 15 ---
--- level 5 --- version# 15 ---
--- level 6 --- version# 15 ---
--- blob files --- version# 15 ---
blob_file_number: 10 total_blob_count: 955 total_blob_bytes: 1014210 checksum_method:  checksum_value:  linked_ssts: { } garbage_blob_count: 0 garbage_blob_bytes: 0
blob_file_number: 13 total_blob_count: 955 total_blob_bytes: 1014210 checksum_method:  checksum_value:  linked_ssts: { } garbage_blob_count: 0 garbage_blob_bytes: 0
blob_file_number: 16 total_blob_count: 955 total_blob_bytes: 1014210 checksum_method:  checksum_value:  linked_ssts: { } garbage_blob_count: 0 garbage_blob_bytes: 0
blob_file_number: 19 total_blob_count: 955 total_blob_bytes: 1014210 checksum_method:  checksum_value:  linked_ssts: { } garbage_blob_count: 0 garbage_blob_bytes: 0
blob_file_number: 22 total_blob_count: 955 total_blob_bytes: 1014210 checksum_method:  checksum_value:  linked_ssts: { } garbage_blob_count: 0 garbage_blob_bytes: 0
blob_file_number: 25 total_blob_count: 955 total_blob_bytes: 1014210 checksum_method:  checksum_value:  linked_ssts: { } garbage_blob_count: 0 garbage_blob_bytes: 0
blob_file_number: 28 total_blob_count: 955 total_blob_bytes: 1014210 checksum_method:  checksum_value:  linked_ssts: { } garbage_blob_count: 0 garbage_blob_bytes: 0
blob_file_number: 31 total_blob_count: 955 total_blob_bytes: 1014210 checksum_method:  checksum_value:  linked_ssts: { } garbage_blob_count: 0 garbage_blob_bytes: 0
blob_file_number: 34 total_blob_count: 955 total_blob_bytes: 1014210 checksum_method:  checksum_value:  linked_ssts: { } garbage_blob_count: 0 garbage_blob_bytes: 0
```
Steps to reproduce the behavior
Run the following code:
```c
#include <iostream>

#include <rocksdb/db.h>
#include <rocksdb/convenience.h>

using namespace rocksdb;

void must_ok(const Status &s) {
    if (!s.ok()) {
        std::cerr << s.ToString() << std::endl;
        exit(EXIT_FAILURE);
    }
}

int main() {
    Options opt;
    opt.create_if_missing = true;
    opt.write_buffer_size = 1024 * 1024;
    opt.target_file_size_base = 1024 * 1024;
    opt.max_bytes_for_level_base = 8 * 1024 * 1024;
    opt.enable_blob_files = true;
    opt.min_blob_size = 512;
    opt.blob_file_size = 1024 * 1024;
    opt.blob_garbage_collection_force_threshold = 0.3;

    DB *db = nullptr;
    must_ok(DB::Open(opt, "./data", &db));

    // Put some data into blobdb
    auto value = std::string(1024, 'a');
    for (int i = 0; i < 10240; ++i)
    {
        char key[32];
        snprintf(key, sizeof(key), "%06d", i);
        must_ok(db->Put(WriteOptions(), key, value));
    }

    // Delete all sst files in the db
    auto s = DeleteFilesInRange(db, db->DefaultColumnFamily(), nullptr, nullptr, true);
    must_ok(s);

    // Show all files in the db, expect no files
    std::string v;
    db->GetProperty("rocksdb.sstables", &v);
    std::cout << v << std::endl;
    return 0;
}
```
## PR 12235
- Fix commit SHA: e28251ca729ed42a5a8d7181b703b2e059506573
- Pre-fix commit SHA: 2dda7a0dd2f2866b85bbbe48a57406b79d7ceb4c

## Steps to Run
- Reproduce.cc
- cd to `rocksdb`
- Run `g++ -o reproduce reproduce.cc -I./include -L. -L/opt/homebrew/lib -lrocksdb -lsnappy -std=c++17` to compile



## Output before fix
```
--- level 0 --- version# 16 ---
 36:20884[8596 .. 9550]['303038353935' seq:8596, type:17 .. '303039353439' seq:9550, type:17] blob_file:37(0)
--- level 1 --- version# 16 ---
--- level 2 --- version# 16 ---
--- level 3 --- version# 16 ---
--- level 4 --- version# 16 ---
--- level 5 --- version# 16 ---
--- level 6 --- version# 16 ---
--- blob files --- version# 16 ---
blob_file_number: 37 total_blob_count: 955 total_blob_bytes: 1014210 checksum_method:  checksum_value:  linked_ssts: { 36 } garbage_blob_count: 0 garbage_blob_bytes: 0
```