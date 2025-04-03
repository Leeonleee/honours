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
