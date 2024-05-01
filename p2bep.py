import argparse
import csv

def na():
    return 'n/a'

def key_to_valence(k):
    if k == 'b': return 'positive'
    if k == 'y': return 'negative'
    return na()

def key_to_gender(k):
    if k == 'b': return 'male'
    if k == 'y': return 'female'
    return na()

def write_baseline(writer, row, t0):
    onset = float(row['baseline.started']) - t0
    duration = float(row['baseline.stopped']) - float(row['baseline.started'])
    event_type = 'baseline'
    writer.writerow([onset, duration, event_type, na(), na(),
                     na(), na(), na(), na(), na()])

def write_prestim_fixation(writer, row, t0):
    onset = float(row['pre_stim_fix.started']) - t0
    duration = float(row['pre_stim_fix.stopped']) - float(row['pre_stim_fix.started'])
    event_type = 'prestim_fixation'
    writer.writerow([onset, duration, event_type, na(), na(),
                     na(), na(), na(), na(), na()])

def write_stim(writer, row, t0):
    onset = float(row['stim.started']) - t0
    duration = float(row['stim.stopped']) - float(row['stim.started'])
    event_type = 'stimulus'
    stim_path = row['stim_path']
    valence = row['Valence']
    key_resp = None
    valence_resp = None
    response_time = None
    if 'valence_resp.keys' in row:
        key_resp = row['valence_resp.keys']
        valence_resp = key_to_valence(key_resp)
        response_time = row['valence_resp.rt']
    writer.writerow([onset, duration, event_type, stim_path, valence,
                     na(), key_resp, valence_resp, na(), response_time])

def write_preface_fixation(writer, row, t0):
    onset = float(row['pre_face_fix.started']) - t0
    duration = float(row['pre_face_fix.stopped']) - float(row['pre_face_fix.started'])
    event_type = 'preface_fixation'
    writer.writerow([onset, duration, event_type, na(), na(),
                     na(), na(), na(), na(), na()])

def write_face(writer, row, t0):
    onset = float(row['neutral_face.started']) - t0
    duration = float(row['neutral_face.stopped']) - float(row['neutral_face.started'])
    event_type = 'neutral_face'
    face_path = row['face_path']
    key_resp = None
    gender_resp = None
    response_time = None
    if 'gender_resp_keys' in row:
        key_resp = row['gender_resp.keys']
        gender_resp = key_to_gender(key_resp)
        response_time = row['gender_resp.rt']
    writer.writerow([onset, duration, event_type, na(), na(),
                     face_path, key_resp, na(), gender_resp, response_time])

def convert(filename):
    with open(filename, encoding='utf-8-sig') as psy_file, \
         open(filename[:-3] + 'first.tsv', 'w', newline='') as first_tsv_file, \
         open(filename[:-3] + 'second.tsv', 'w', newline='') as second_tsv_file:
        
        reader = csv.DictReader(psy_file)
        writer = None

        headers = ['onset', 'duration', 'event_type', 'stim_path', 'valence',
                   'face_path', 'key_resp', 'valence_resp', 'gender_resp', 'resp_time']

        t0_first_half = None
        t0_second_half = None
        t0_current_half = None

        for row in reader:
            ttl_2nd_half_key = 'key_resp_7.keys' if 'key_resp_7.keys' in row else 'pulse_key.keys'
            if row['key_resp_2.started']:
                t0_first_half = float(row['key_resp_2.started']) + float(row['key_resp_2.rt'])
                t0_current_half = t0_first_half
                writer = csv.writer(first_tsv_file, delimiter='\t', lineterminator='\n')
                writer.writerow(headers)
            if row[ttl_2nd_half_key] == 't':
                t0_second_half = float(row['trial.started'])
                t0_current_half = t0_second_half
                writer = csv.writer(second_tsv_file, delimiter='\t', lineterminator='\n')
                writer.writerow(headers)
            if row['stim_path']:
                if row['baseline.started']:
                    write_baseline(writer, row, t0_current_half)
                write_prestim_fixation(writer, row, t0_current_half)
                write_stim(writer, row, t0_current_half)
                write_preface_fixation(writer, row, t0_current_half)
                write_face(writer, row, t0_current_half)

def main():
    parser = argparse.ArgumentParser(
        prog='p2bep',
        description='BIDSify PsychoPy data from EP fMRI task',
    )
    parser.add_argument('filename', type=str)
    args = parser.parse_args()
    filename = args.filename
    convert(filename)

if __name__ == '__main__':
    main()