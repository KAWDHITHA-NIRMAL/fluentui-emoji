import os
import json

def rename_and_generate_metadata():
    assets_dir = 'assets'
    
    if not os.path.exists(assets_dir) or not os.path.isdir(assets_dir):
        print(f"Error: '{assets_dir}' directory not found in the current root.")
        return

    # 1. Rename folders and files to replace spaces with hyphens
    print("Step 1: Renaming folders and files (replacing spaces with hyphens)...")
    
    for root, dirs, files in os.walk(assets_dir, topdown=False):
        for name in files:
            if ' ' in name:
                new_name = name.replace(' ', '-')
                old_path = os.path.join(root, name)
                new_path = os.path.join(root, new_name)
                if not os.path.exists(new_path):
                    os.rename(old_path, new_path)

        for name in dirs:
            if ' ' in name:
                new_name = name.replace(' ', '-')
                old_path = os.path.join(root, name)
                new_path = os.path.join(root, new_name)
                if not os.path.exists(new_path):
                    os.rename(old_path, new_path)

    print("Renaming completed.")

    # 2. Scan and generate metadata.json
    print("Step 2: Generating consolidated metadata.json...")
    
    all_metadata = []
    asset_folders = sorted([f for f in os.listdir(assets_dir) if os.path.isdir(os.path.join(assets_dir, f))])

    print(f"Processing {len(asset_folders)} assets...")

    # Style folders we look for
    STYLE_FOLDERS = ["3D", "Color", "Flat", "High-Contrast"]
    # Skin tone variant folders
    SKIN_TONE_FOLDERS = ["Default", "Dark", "Light", "Medium", "Medium-Dark", "Medium-Light"]

    for folder_name in asset_folders:
        folder_path = os.path.join(assets_dir, folder_name)
        metadata_file = os.path.join(folder_path, 'metadata.json')

        # Load original metadata
        asset_info = {}
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    asset_info = json.load(f)
            except Exception:
                asset_info = {"name": folder_name}
        else:
            asset_info = {"name": folder_name}

        # Collect variations
        variations = {}

        # Check if style folders exist directly (simple emojis like "Red apple")
        has_direct_styles = any(
            os.path.isdir(os.path.join(folder_path, s)) for s in STYLE_FOLDERS
        )

        if has_direct_styles:
            # Simple structure: assets/Emoji/3D/file.png
            for style in STYLE_FOLDERS:
                style_path = os.path.join(folder_path, style)
                if os.path.isdir(style_path):
                    files = [
                        f"assets/{folder_name}/{style}/{f}"
                        for f in os.listdir(style_path)
                        if f.lower().endswith(('.png', '.svg'))
                    ]
                    if files:
                        variations[style] = files
        else:
            # Skin tone structure: assets/Emoji/Default/3D/file.png
            # Check each skin tone subfolder
            subfolders = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d)) and d != '__pycache__']
            
            for subfolder in sorted(subfolders):
                subfolder_path = os.path.join(folder_path, subfolder)
                
                # Check if this subfolder contains style folders
                has_styles = any(
                    os.path.isdir(os.path.join(subfolder_path, s)) for s in STYLE_FOLDERS
                )
                
                if has_styles:
                    for style in STYLE_FOLDERS:
                        style_path = os.path.join(subfolder_path, style)
                        if os.path.isdir(style_path):
                            files = [
                                f"assets/{folder_name}/{subfolder}/{style}/{f}"
                                for f in os.listdir(style_path)
                                if f.lower().endswith(('.png', '.svg'))
                            ]
                            if files:
                                # Key format: "Default/3D", "Dark/Color", etc.
                                key = f"{subfolder}/{style}"
                                variations[key] = files

        asset_info['variations'] = variations
        all_metadata.append(asset_info)

    # Save to root metadata.json
    output_filename = 'metadata.json'
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, indent=2, ensure_ascii=False)
        print(f"Success! Root metadata file created: {output_filename}")
        print(f"Total assets processed: {len(all_metadata)}")
    except Exception as e:
        print(f"Error saving {output_filename}: {e}")

if __name__ == "__main__":
    rename_and_generate_metadata()
