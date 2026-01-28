import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pprint

data_path = "/Users/macbook/desktop/škola/JSP3 a JPC1/sentiment data.json"


def read_json(file_path):
    """Loads a JSON file and returns its content as a Python dictionary or list."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def graph_block_and_chapters_sentiment(data):
    """
    - Neutral sentiment (gray dashed line)
    - Chapter boundaries (dashed vertical lines)
    - Sentiment methods (colored lines)
    - Average sentiment (red)
    - Sentiment of blocks (dots/curves)
    - Sentiment of chapters (horizontal lines)
    """

    def darken(color, factor=0.9):
        return tuple(c * factor for c in color)

    # --- BLOCKS ---
    block_positions = np.array(sorted(map(int, data["block_locations"].keys())))
    block_values = np.array([data["block_locations"][str(pos)] for pos in block_positions])
    n_methods = block_values.shape[1]

    block_methods = [block_values[:, i] for i in range(n_methods)]
    block_avg = block_values.mean(axis=1)

    block_width = block_positions[0]
    half_width = block_width / 2
    end_x = block_positions[-1] + block_width

    # --- CHAPTERS ---
    chapter_positions = np.array(sorted(map(int, data["chapter_locations"].keys())))
    chapter_values = np.array([data["chapter_locations"][str(pos)] for pos in chapter_positions])
    chapter_avg = chapter_values.mean(axis=1)

    # --- PLOT SETUP ---
    plt.figure(figsize=(13, 6))

    all_values = np.concatenate([block_values.flatten(), chapter_values.flatten()])
    y_min, y_max = np.min(all_values), np.max(all_values)
    padding = (y_max - y_min) * 0.05
    plt.ylim(y_min - padding, y_max + padding)

    # Neutral sentiment line
    plt.axhline(0, color="gray", linestyle=":", linewidth=1.5)

    colors = plt.cm.tab10.colors

    # --- BLOCKS LINES AND POINTS ---
    for i, method in enumerate(block_methods):
        x = np.concatenate(([0], block_positions, [end_x]))
        y = np.concatenate(([0], method, [0]))
        color = colors[i % len(colors)]
        plt.plot(x, y, color=color, linewidth=2, alpha=0.9)
        plt.scatter(x[1:-1], y[1:-1], color=color, s=50)

    # Average of blocks (red)
    x_avg = np.concatenate(([0], block_positions, [end_x]))
    y_avg = np.concatenate(([0], block_avg, [0]))
    plt.plot(x_avg, y_avg, color="red", linewidth=3)
    plt.scatter(x_avg[1:-1], y_avg[1:-1], color="red", s=60)

    # --- CHAPTERS LINES ---
    prev_x = 0
    for i, chap_pos in enumerate(chapter_positions):
        end_chap_x = end_x if i == len(chapter_positions) - 1 else chap_pos
        center_x = (prev_x + end_chap_x) / 2

        # Chapter boundaries
        if i != len(chapter_positions) - 1:
            plt.axvline(chap_pos, linestyle="--", color="gray", alpha=0.6)

        # Short horizontal lines for each method in chapter
        for m in range(n_methods):
            base_color = colors[m % len(colors)]
            dark_color = darken(base_color)
            plt.hlines(
                chapter_values[i, m],
                center_x - half_width,
                center_x + half_width,
                color=dark_color,
                linewidth=4,
                alpha=0.95,
                capstyle="round",
                zorder=4
            )

        # Average sentiment of chapter (red, for average of methods, "in words")
        plt.hlines(
            chapter_avg[i],
            center_x - half_width,
            center_x + half_width,
            color="red",
            linewidth=5,
            alpha=0.9,
            capstyle="round",
            zorder=5
        )

        # Optional gray short line for visual reference (general)
        plt.hlines(
            chapter_avg[i],
            center_x - half_width,
            center_x + half_width,
            color="gray",
            linewidth=5,
            alpha=0.3,
            capstyle="round",
            zorder=3
        )

        prev_x = chap_pos

    # --- LEGEND PROXY ELEMENTS ---
    legend_elements = [
        Line2D([0], [0], color="gray", linestyle=":", lw=1.5, label="Neutral sentiment"),
        Line2D([0], [0], linestyle='--', color="gray", lw=2, label="Chapter boundaries")
    ]

    # Block methods
    for i in range(n_methods):
        legend_elements.append(Line2D([0], [0], color=colors[i % len(colors)], lw=2, label=f"Method {i+1}"))

    # Average methods (red)
    legend_elements.append(Line2D([0], [0], color="red", lw=3, label="Average of methods"))

    # Average sentiment of blocks (gray dot)
    legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=8,
                                  label="Average sentiment of blocks (generally)"))

    # Average sentiment of chapters (gray short horizontal line)
    legend_elements.append(Line2D([0], [0], color='gray', lw=5, alpha=0.3, solid_capstyle='round',
                                  label="Average sentiment of chapters (generally)"))

    plt.legend(handles=legend_elements, loc="upper left")

    plt.xlim(0, max(end_x, max(chapter_positions)))
    plt.xlabel("Position in words")
    plt.ylabel("Sentiment")
    plt.title("Block and Chapter Sentiment")
    plt.tight_layout()
    plt.show()


def main():
    data = read_json(data_path)
    pprint.pprint(data)

    graph_block_and_chapters_sentiment(data)

if __name__ == "__main__":
    main()

