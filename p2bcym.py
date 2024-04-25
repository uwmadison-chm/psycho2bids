import argparse
import csv

def write_first_fixation(writer, row, t0):
    onset = float(row['fixation_one.started']) - t0
    duration = float(row['fixation_one.stopped']) - float(row['fixation_one.started'])
    trial_type = 'difficult' if row['isDifficult'] == '1' else 'easy'
    writer.writerow([onset, duration, 'n/a', 'n/a', row['targetLetter'], 'fixation1', trial_type, 'n/a', 'n/a', 'n/a', 'n/a'])

def write_first_half(writer, row, t0):
    onset = float(row['target.started']) - t0
    duration = float(row['target.stopped']) - float(row['target.started'])
    onset_masked = float(row['target_masked.started']) - t0
    duration_masked = float(row['target_masked.stopped']) - float(row['target_masked.started'])
    trial_type = 'difficult' if row['isDifficult'] == '1' else 'easy'
    response_time = "n/a" if not row['resp_one.rt'] else row['resp_one.rt']
    correct = is_correct(row['targetLetter'], row['resp_one.keys'])
    writer.writerow([onset, duration, onset_masked, duration_masked, row['targetLetter'], 'probe1', trial_type, response_time, correct, 'n/a', 'n/a'])

def write_feedback(writer, row, t0):
    onset = float(row['feedback.started']) - t0
    duration = float(row['feedback.stopped']) - float(row['feedback.started'])
    trial_type = 'difficult' if row['isDifficult'] == '1' else 'easy'
    response_time = "n/a"
    correct = is_correct(row['targetLetter'], row['resp_one.keys'])
    writer.writerow([onset, duration, 'n/a', 'n/a', row['targetLetter'], 'feedback', trial_type, response_time, 'n/a',
                     feedback_text(row['accurateFeedback'] == '1', correct), row['accurateFeedback']])
    
def write_second_fixation(writer, row, t0):
    onset = float(row['fixation_two.started']) - t0
    duration = float(row['fixation_two.stopped']) - float(row['fixation_two.started'])
    trial_type = 'difficult' if row['isDifficult'] == '1' else 'easy'
    writer.writerow([onset, duration, 'n/a', 'n/a', row['targetLetter'], 'fixation2', trial_type, 'n/a', 'n/a', 'n/a', 'n/a'])

def write_second_half(writer, row, t0):
    onset = float(row['target_two.started']) - t0
    duration = float(row['target_two.stopped']) - float(row['target_two.started'])
    onset_masked = float(row['target_masked_two.started']) - t0
    duration_masked = float(row['target_masked_two.stopped']) - float(row['target_masked_two.started'])
    trial_type = 'difficult' if row['isDifficult'] == '1' else 'easy'
    response_time = "n/a" if not row['resp_two.rt'] else row['resp_two.rt']
    correct = is_correct(row['targetLetter'], row['resp_two.keys'])
    writer.writerow([onset, duration, onset_masked, duration_masked, row['targetLetter'], 'probe2', trial_type, response_time, correct, 'n/a', 'n/a'])

def is_correct(target, key):
    return (target == 'T' and key == 'b') or (target == 'L' and key == 'y')

def feedback_text(is_accurate, is_correct):
    if is_accurate == is_correct:
        return "correct"
    return "wrong"

def convert(filename):
    with open(filename, encoding='utf-8-sig') as psy_file, \
         open(filename[:-3] + 'first.tsv', 'w', newline='') as first_tsv_file, \
         open(filename[:-3] + 'second.tsv', 'w', newline='') as second_tsv_file:
        
        reader = csv.DictReader(psy_file)
        writer = None

        headers = ['onset', 'duration', 'onset_masked', 'duration_masked', 'target_letter', 'event_type', 'trial_type', 'response_time', 'correct', 'feedback_text', 'feedback_accurate']

        t0_first_half = None
        t0_second_half = None
        t0_current_half = None

        for row in reader:
            if row['key_resp_3.started']:
                t0_first_half = float(row['key_resp_3.started']) + float(row['key_resp_3.rt'])
                t0_current_half = t0_first_half
                writer = csv.writer(first_tsv_file, delimiter='\t', lineterminator='\n')
                writer.writerow(headers)
            if row['key_resp_6.keys'] == 't':
                t0_second_half = float(row['break_countdown.started'])
                t0_current_half = t0_second_half
                writer = csv.writer(second_tsv_file, delimiter='\t', lineterminator='\n')
                writer.writerow(headers)
            if row['targetLetter']:
                write_first_fixation(writer, row, t0_current_half)
                write_first_half(writer, row, t0_current_half)
                write_feedback(writer, row, t0_current_half)
                write_second_fixation(writer, row, t0_current_half)
                write_second_half(writer, row, t0_current_half)


def main():
    parser = argparse.ArgumentParser(
        prog='p2bcym',
        description='BIDSify PsychoPy data from CYM fMRI task',
    )
    parser.add_argument('filename', type=str)
    args = parser.parse_args()
    filename = args.filename
    convert(filename)

if __name__ == '__main__':
    main()