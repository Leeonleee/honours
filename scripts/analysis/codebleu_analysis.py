from codebleu import calc_codebleu

prediction = """
--- a/src/common/types/vector.cpp
+++ b/src/common/types/vector.cpp
@@ -1674,6 +1674,9 @@
 		TemplatedSearchInMap<double>(list, key, offsets, key.IsNull(), entry.offset, entry.length);
 		break;
 	case PhysicalType::VARCHAR:
 		SearchStringInMap(list, StringValue::Get(key), offsets, key.IsNull(), entry.offset, entry.length);
 		break;
+	case PhysicalType::INTERVAL:
+		TemplatedSearchInMap<interval_t>(list, key, offsets, key.IsNull(), entry.offset, entry.length);
+		break;
 	default:
 		throw InvalidTypeException(list.GetType().id(), "Invalid type for List Vector Search");
 	}
+
"""
reference = """
diff --git a/src/common/types/vector.cpp b/src/common/types/vector.cpp
index ff88d59b6db9..7ab577a7d40f 100644
--- a/src/common/types/vector.cpp
+++ b/src/common/types/vector.cpp
@@ -1674,6 +1674,9 @@ vector<idx_t> ListVector::Search(Vector &list, const Value &key, idx_t row) {
 	case PhysicalType::DOUBLE:
 		TemplatedSearchInMap<double>(list, key, offsets, key.IsNull(), entry.offset, entry.length);
 		break;
+	case PhysicalType::INTERVAL:
+		TemplatedSearchInMap<interval_t>(list, key, offsets, key.IsNull(), entry.offset, entry.length);
+		break;
 	case PhysicalType::VARCHAR:
 		SearchStringInMap(list, StringValue::Get(key), offsets, key.IsNull(), entry.offset, entry.length);
 		break;

"""

result = calc_codebleu([reference], [prediction], lang="python", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
print(result)
# {
#   'codebleu': 0.5537, 
#   'ngram_match_score': 0.1041, 
#   'weighted_ngram_match_score': 0.1109, 
#   'syntax_match_score': 1.0, 
#   'dataflow_match_score': 1.0
# }