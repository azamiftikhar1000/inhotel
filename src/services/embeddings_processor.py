def get_value_or_default(data, key, default_value):
    value = data.get(key, default_value) or default_value
    if isinstance(value, list):
        value = ",".join([str(v) for v in value])
    else:
        value = str(value)
    return value


class EmbeddingsProcessor:
    def __init__(self, embeddings_model, milvus_manager):
        self.embeddings_model = embeddings_model
        self.milvus_manager = milvus_manager

    def process_and_save(self, S3_URI, data_dict):
        object_id = data_dict.get("id")

        document_summary = data_dict.get("document_summary", "")
        if document_summary and len(document_summary) > 20 and False:
            # Todo we can review this if we want document summary to be used in search more often
            meta_data = f"Title :{get_value_or_default(data_dict, 'title', '')} \n Summary: {document_summary}"
        else:
            meta_data = f"Title :{get_value_or_default(data_dict, 'title', '')} \n Description :{get_value_or_default(data_dict, 'description', '')}"
        duration = get_value_or_default(data_dict, "duration", "")
        age_min = int(get_value_or_default(data_dict, "age_min", 0))
        age_max = int(get_value_or_default(data_dict, "age_max", 0))
        core_subject = get_value_or_default(data_dict, "core_subject", "")
        subject_area = get_value_or_default(data_dict, "subject_area", "")
        type_val = get_value_or_default(data_dict, "type", "")
        grade_levels = data_dict.get("grade_level", [])
        interests = get_value_or_default(data_dict, "interests", "")
        materials = get_value_or_default(data_dict, "materials", "")
        unit = get_value_or_default(data_dict, "unit", "")
        topic = get_value_or_default(data_dict, "topic", "")
        
        title = get_value_or_default(data_dict, 'title', 'This document')
        description = get_value_or_default(data_dict, 'description', '')

        vector_text_data = f"'{title}' is about {description}. "

        if core_subject:
            vector_text_data += f"The primary focus is on {core_subject}. "

        if subject_area:
            vector_text_data += f"This falls under the broader area of {subject_area}. "

        if type_val:
            vector_text_data += f"The format is {type_val}. "

        if grade_levels:
            vector_text_data += f"It's suitable for grades: {', '.join([str(grade_level) for grade_level in grade_levels])}. "

        if interests:
            vector_text_data += f"People interested in {interests} might find this appealing. "

        embedding_vector = self.embeddings_model.embed_query(vector_text_data)
        result = self.milvus_manager.insert(
            object_id,
            embedding_vector,
            S3_URI,
            meta_data,
            duration,
            age_min,
            age_max,
            core_subject,
            subject_area,
            type_val,
            grade_levels,
            interests,
            materials,
            unit,
            topic,
        )
        return result

    def process_and_search(self, query_list, filters=None, top_k=None):
        embedding_vector_list = self.embeddings_model.embed_query(query_list[0])
        result = self.milvus_manager.search([embedding_vector_list], filters, top_k)
        return result
