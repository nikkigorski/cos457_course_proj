#!/usr/bin/env python3

import argparse
import json
import sys
import re
import datetime
from decimal import Decimal, InvalidOperation


URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def check_resource(row, errors, warnings, idx):
    # ResourceID
    rid = row.get('ResourceID')
    if not is_int(rid):
        errors.append((f'Resource[{idx}]', 'ResourceID missing or not integer'))

    # Date and DateFor must be iso dates
    for dkey in ('Date', 'DateFor'):
        v = row.get(dkey)
        if not isinstance(v, str):
            errors.append((f'Resource[{idx}]', f'{dkey} missing or not a string'))
        else:
            try:
                datetime.date.fromisoformat(v)
            except Exception:
                errors.append((f'Resource[{idx}]', f'{dkey} not ISO date (YYYY-MM-DD): {v}'))

    # Author: varchar(50) not null
    author = row.get('Author')
    if not author or not isinstance(author, str):
        errors.append((f'Resource[{idx}]', 'Author missing or not a string'))
    else:
        if len(author) > 50:
            errors.append((f'Resource[{idx}]', f'Author too long ({len(author)} > 50)'))

    # Topic: varchar(25) not null
    topic = row.get('Topic')
    if not topic or not isinstance(topic, str):
        errors.append((f'Resource[{idx}]', 'Topic missing or not a string'))
    else:
        if len(topic) > 25:
            errors.append((f'Resource[{idx}]', f'Topic too long ({len(topic)} > 25)'))

    # Keywords: nullable varchar(25)
    kw = row.get('Keywords')
    if kw is not None and not isinstance(kw, str):
        errors.append((f'Resource[{idx}]', 'Keywords present but not a string'))
    if isinstance(kw, str) and len(kw) > 25:
        errors.append((f'Resource[{idx}]', f'Keywords too long ({len(kw)} > 25)'))

    # Rating numeric(2,1) -- allow 0.0..9.9 to fit (2 total digits, 1 decimal)
    rating = row.get('Rating')
    if rating is not None:
        try:
            d = Decimal(str(rating))
            if d < Decimal('0.0') or d > Decimal('9.9'):
                errors.append((f'Resource[{idx}]', f'Rating out of range 0.0-9.9: {rating}'))
        except (InvalidOperation, ValueError):
            errors.append((f'Resource[{idx}]', f'Rating not numeric: {rating}'))

    # Format enum
    fmt = row.get('Format')
    allowed = {'Note', 'Video', 'Website', 'Pdf', 'Image'}
    if not fmt or not isinstance(fmt, str) or fmt not in allowed:
        errors.append((f'Resource[{idx}]', f'Format missing or invalid (allowed: {sorted(allowed)}): {fmt}'))

    # isVerified boolean or null
    iv = row.get('isVerified')
    if iv is not None and not isinstance(iv, bool):
        errors.append((f'Resource[{idx}]', 'isVerified present but not boolean'))


def check_note(row, errors, warnings, idx, resource_ids, table_name='Note'):
    rid = row.get('ResourceID')
    if not is_int(rid):
        errors.append((f'{table_name}[{idx}]', 'ResourceID missing or not integer'))
    else:
        if rid not in resource_ids:
            errors.append((f'{table_name}[{idx}]', f'ResourceID {rid} has no matching Resource'))
    body = row.get('Body')
    if not isinstance(body, str):
        errors.append((f'{table_name}[{idx}]', 'Body missing or not a string'))
    else:
        if len(body) > 2048:
            errors.append((f'{table_name}[{idx}]', f'Body too long ({len(body)} > 2048)'))


def check_pdf(row, errors, warnings, idx, resource_ids):
    rid = row.get('ResourceID')
    if not is_int(rid):
        errors.append((f'{table_name}[{idx}]', 'ResourceID missing or not integer'))
    else:
        if rid not in resource_ids:
            errors.append((f'{table_name}[{idx}]', f'ResourceID {rid} has no matching Resource'))
    body = row.get('Body')
    if not isinstance(body, str):
        errors.append((f'{table_name}[{idx}]', 'Body missing or not a string'))
    else:
        if len(body) > 2048:
            errors.append((f'{table_name}[{idx}]', f'Body too long ({len(body)} > 2048)'))


def check_image(row, errors, warnings, idx, resource_ids):
    rid = row.get('ResourceID')
    if not is_int(rid):
        errors.append((f'Image[{idx}]', 'ResourceID missing or not integer'))
    else:
        if rid not in resource_ids:
            errors.append((f'Image[{idx}]', f'ResourceID {rid} has no matching Resource'))

    size = row.get('Size')
    if size is None:
        warnings.append((f'Image[{idx}]', 'Size column expected by DB is missing in JSON '))
    else:
        if not is_int(size) or size <= 0:
            errors.append((f'Image[{idx}]', f'Size must be a positive integer, got: {size}'))

    link = row.get('Link')
    if link is not None:
        if not isinstance(link, str) or not URL_RE.match(link):
            errors.append((f'Image[{idx}]', f'Link is present but not a valid http(s) URL: {link}'))


def check_video(row, errors, warnings, idx, resource_ids):
    rid = row.get('ResourceID')
    if not is_int(rid):
        errors.append((f'Video[{idx}]', 'ResourceID missing or not integer'))
    else:
        if rid not in resource_ids:
            errors.append((f'Video[{idx}]', f'ResourceID {rid} has no matching Resource'))

    dur = row.get('Duration')
    if not is_int(dur) or dur <= 0:
        errors.append((f'Video[{idx}]', f'Duration must be positive integer (>0); got: {dur}'))

    link = row.get('Link')
    if link is not None:
        if not isinstance(link, str) or (link and not URL_RE.match(link)):
            errors.append((f'Video[{idx}]', f'Link must be null or an http(s) URL: {link}'))


def check_website(row, errors, warnings, idx, resource_ids):
    rid = row.get('ResourceID')
    if not is_int(rid):
        errors.append((f'Website[{idx}]', 'ResourceID missing or not integer'))
    else:
        if rid not in resource_ids:
            errors.append((f'Website[{idx}]', f'ResourceID {rid} has no matching Resource'))

    link = row.get('Link')
    if not isinstance(link, str) or not URL_RE.match(link):
        errors.append((f'Website[{idx}]', f'Link missing or invalid http(s) URL: {link}'))


def validate(data):
    errors = []
    warnings = []

    # expected top-level keys
    expected = {'Resource', 'Note', 'pdf', 'Image', 'Video', 'Website'}
    present = set(k for k in data.keys())
    missing = expected - present
    if missing:
        warnings.append(('top-level', f'Missing expected sections: {sorted(list(missing))}'))

    resources = data.get('Resource', []) or []
    notes = data.get('Note', []) or []
    pdfs = data.get('pdf', []) or []
    images = data.get('Image', []) or []
    videos = data.get('Video', []) or []
    websites = data.get('Website', []) or []

    # Validate Resource entries
    resource_ids = set()
    for idx, r in enumerate(resources):
        if not isinstance(r, dict):
            errors.append((f'Resource[{idx}]', 'Resource entry is not an object'))
            continue
        check_resource(r, errors, warnings, idx)
        rid = r.get('ResourceID')
        if is_int(rid):
            if rid in resource_ids:
                errors.append((f'Resource[{idx}]', f'Duplicate ResourceID {rid}'))
            resource_ids.add(rid)

    # Validate child tables
    for idx, n in enumerate(notes):
        if not isinstance(n, dict):
            errors.append((f'Note[{idx}]', 'entry not an object'))
            continue
        check_note(n, errors, warnings, idx, resource_ids)

    for idx, p in enumerate(pdfs):
        if not isinstance(p, dict):
            errors.append((f'pdf[{idx}]', 'entry not an object'))
            continue
        check_pdf(p, errors, warnings, idx, resource_ids)

    for idx, im in enumerate(images):
        if not isinstance(im, dict):
            errors.append((f'Image[{idx}]', 'entry not an object'))
            continue
        check_image(im, errors, warnings, idx, resource_ids)

    for idx, v in enumerate(videos):
        if not isinstance(v, dict):
            errors.append((f'Video[{idx}]', 'entry not an object'))
            continue
        check_video(v, errors, warnings, idx, resource_ids)

    for idx, w in enumerate(websites):
        if not isinstance(w, dict):
            errors.append((f'Website[{idx}]', 'entry not an object'))
            continue
        check_website(w, errors, warnings, idx, resource_ids)

    return errors, warnings


def main():
    p = argparse.ArgumentParser()
    p.add_argument('jsonfile')
    args = p.parse_args()

    try:
        data = load_json(args.jsonfile)
    except Exception as e:
        print(f'ERROR: failed to read JSON file: {e}', file=sys.stderr)
        sys.exit(2)

    errors, warnings = validate(data)

    if warnings:
        print('\nWarnings:')
        for src, msg in warnings:
            print(f'  - {src}: {msg}')

    if errors:
        print('\nErrors:')
        for src, msg in errors:
            print(f'  - {src}: {msg}')
        print(f'\nValidation FAILED: {len(errors)} error(s), {len(warnings)} warning(s)')
        sys.exit(1)
    else:
        print(f'Validation OK: no errors, {len(warnings)} warning(s)')
        sys.exit(0)


if __name__ == '__main__':
    main()
