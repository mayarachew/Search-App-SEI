import pandas as pd
import ast
from collections import defaultdict

def extract_entities(tokens, labels):
    entities = defaultdict(list)
    entity = []
    entity_type = None

    for token, label in zip(tokens, labels):
        if label.startswith("B-"):
            if entity and entity_type:
                entities[entity_type].append(" ".join(entity))
            entity_type = label[2:]
            entity = [token]
        elif label.startswith("I-") and entity_type == label[2:]:
            entity.append(token)
        else:
            if entity and entity_type:
                entities[entity_type].append(" ".join(entity))
            entity = []
            entity_type = None

    if entity and entity_type:
        entities[entity_type].append(" ".join(entity))

    return entities

def convert_csv(input_path, output_path):
    df = pd.read_csv(input_path)
    output_rows = []

    for _, row in df.iterrows():
        sentence_id = row['id']
        tokens = ast.literal_eval(row['sentence'])
        labels = ast.literal_eval(row['predicted_label'])
        entities = extract_entities(tokens, labels)

        output_row = {
            "id": sentence_id,
            "sentence": str(tokens),  # Preserve list format
            "predicted_label": str(labels),  # Preserve list format
        }

        # Add each entity type column
        for entity_type, entity_list in entities.items():
            output_row[entity_type] = "; ".join(entity_list)

        output_rows.append(output_row)

    # Create DataFrame from processed rows
    output_df = pd.DataFrame(output_rows)

    # Ensure consistent column order
    entity_columns = sorted({col for row in output_rows for col in row if col not in ("id", "sentence", "predicted_label")})
    output_df = output_df[["id", "sentence", "predicted_label"] + entity_columns]

    output_df.to_csv(output_path, index=False)
    print(f"Converted CSV saved to: {output_path}")


convert_csv("resolutions_pred.csv", "structured/p_resolutions.csv")
