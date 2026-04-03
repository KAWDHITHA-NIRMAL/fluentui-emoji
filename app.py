from flask import Flask, request, send_from_directory, Response
import json
import os

app = Flask(__name__)

# Load metadata.json once at startup
METADATA = []
metadata_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metadata.json')

with open(metadata_path, 'r', encoding='utf-8') as f:
    METADATA = json.load(f)

print(f"Loaded {len(METADATA)} emojis from metadata.json")


def json_response(data, status=200):
    """Custom JSON response that shows actual emoji characters instead of escaped unicode"""
    # Add creator & developer info to every response
    data["creator"] = "Kawdhitha Nirmal"
    data["developers"] = "Cyber Yakku"
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        status=status,
        mimetype='application/json; charset=utf-8'
    )


def add_url_prefix(emoji_list):
    """Add full server URL prefix to all asset paths in variations"""
    base_url = request.host_url.rstrip('/')
    result = []
    for emoji in emoji_list:
        e = dict(emoji)  # shallow copy
        if 'variations' in e:
            new_variations = {}
            for style, paths in e['variations'].items():
                new_variations[style] = [f"{base_url}/{p}" for p in paths]
            e['variations'] = new_variations
        result.append(e)
    return result


# ─────────────────────────────────────────────
# GET /api/emojis
#   → Returns all emojis
#   → ?search=<query>  searches keywords, mappedToEmoticons, glyph, cldr
# ─────────────────────────────────────────────
@app.route('/api/emojis', methods=['GET'])
def get_emojis():
    search = request.args.get('search', '').strip().lower()

    if not search:
        # Return all emojis
        emojis = add_url_prefix(METADATA)
        return json_response({
            "total": len(METADATA),
            "emojis": emojis
        })

    # Search logic
    results = []
    for emoji in METADATA:
        matched = False

        # 1. Check glyph (exact)
        if emoji.get('glyph', '') == search or emoji.get('glyph', '').lower() == search:
            matched = True

        # 2. Check cldr name (partial, case-insensitive)
        if not matched and search in emoji.get('cldr', '').lower():
            matched = True

        # 3. Check keywords (partial, case-insensitive)
        if not matched:
            for kw in emoji.get('keywords', []):
                if search in kw.lower():
                    matched = True
                    break

        # 4. Check mappedToEmoticons (partial, case-insensitive)
        if not matched:
            for em in emoji.get('mappedToEmoticons', []):
                if search in em.lower():
                    matched = True
                    break

        # 5. Check tts (partial, case-insensitive)
        if not matched and search in emoji.get('tts', '').lower():
            matched = True

        if matched:
            results.append(emoji)

    return json_response({
        "search": search,
        "total": len(results),
        "emojis": add_url_prefix(results)
    })


# ─────────────────────────────────────────────
# GET /api/emojis/group
#   → Returns all unique group names
#   → ?name=<GroupName>  returns emojis in that group
# ─────────────────────────────────────────────
@app.route('/api/emojis/group', methods=['GET'])
def get_groups():
    group_name = request.args.get('name', '').strip()

    if not group_name:
        # Return all unique group names
        groups = sorted(set(e.get('group', 'Unknown') for e in METADATA))
        return json_response({
            "total": len(groups),
            "groups": groups
        })

    # Filter emojis by group name (case-insensitive)
    results = [e for e in METADATA if e.get('group', '').lower() == group_name.lower()]

    return json_response({
        "group": group_name,
        "total": len(results),
        "emojis": add_url_prefix(results)
    })


# ─────────────────────────────────────────────
# Serve asset files (png/svg) directly
# ─────────────────────────────────────────────
@app.route('/assets/<path:filepath>')
def serve_asset(filepath):
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
    return send_from_directory(assets_dir, filepath)


# ─────────────────────────────────────────────
# Root route — API info
# ─────────────────────────────────────────────
@app.route('/')
def index():
    return json_response({
        "name": "FluentUI Emoji API",
        "version": "1.0.0",
        "endpoints": {
            "all_emojis": "/api/emojis",
            "search_emojis": "/api/emojis?search=<query>",
            "all_groups": "/api/emojis/group",
            "group_emojis": "/api/emojis/group?name=<GroupName>"
        },
        "total_emojis": len(METADATA)
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
