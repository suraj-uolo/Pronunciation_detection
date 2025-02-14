import matplotlib.pyplot as plt

def visualize_phonemes(phoneme_timestamps):
    """
    Visualizes phoneme timestamps on a timeline.
    
    Parameters:
    phoneme_timestamps (list): List of dictionaries with 'phoneme', 'start', and 'end' keys.
    """
    phonemes = [p['phoneme'] for p in phoneme_timestamps]
    starts = [p['start'] for p in phoneme_timestamps]
    ends = [p['end'] for p in phoneme_timestamps]

    # Create a timeline for phonemes
    plt.figure(figsize=(12, 4))
    for i, (phoneme, start, end) in enumerate(zip(phonemes, starts, ends)):
        plt.hlines(y=1, xmin=start, xmax=end, linewidth=8, label=phoneme)
        plt.text((start + end) / 2, 1.05, phoneme, ha='center', va='bottom', fontsize=10)

    plt.title("Phoneme Timeline")
    plt.xlabel("Time (seconds)")
    plt.yticks([])
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=5, fontsize=8)
    plt.tight_layout()
    plt.show()
def visualize_alignment(word_timestamps, phoneme_timestamps):
    """
    Visualizes word and phoneme alignment on a timeline.
    
    Parameters:
    word_timestamps (list): List of dictionaries with 'word', 'start', and 'end' keys.
    phoneme_timestamps (list): List of dictionaries with 'phoneme', 'start', and 'end' keys.
    """
    words = [w['word'] for w in word_timestamps]
    word_starts = [w['start'] for w in word_timestamps]
    word_ends = [w['end'] for w in word_timestamps]

    phonemes = [p['phoneme'] for p in phoneme_timestamps]
    phoneme_starts = [p['start'] for p in phoneme_timestamps]
    phoneme_ends = [p['end'] for p in phoneme_timestamps]

    plt.figure(figsize=(12, 6))

    # Plot word alignment
    for i, (word, start, end) in enumerate(zip(words, word_starts, word_ends)):
        plt.hlines(y=2, xmin=start, xmax=end, linewidth=10, color='blue', alpha=0.5, label='Word' if i == 0 else "")
        plt.text((start + end) / 2, 2.1, word, ha='center', va='bottom', fontsize=10, color='blue')

    # Plot phoneme alignment
    for i, (phoneme, start, end) in enumerate(zip(phonemes, phoneme_starts, phoneme_ends)):
        plt.hlines(y=1, xmin=start, xmax=end, linewidth=8, color='orange', alpha=0.7, label='Phoneme' if i == 0 else "")
        plt.text((start + end) / 2, 1.05, phoneme, ha='center', va='bottom', fontsize=8, color='orange')

    plt.title("Word-to-Audio Alignment")
    plt.xlabel("Time (seconds)")
    plt.yticks([1, 2], ["Phonemes", "Words"])
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=10)
    plt.tight_layout()
    plt.show()