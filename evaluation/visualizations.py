# ============================================================
# EVALUATION MODULE — visualizations.py
# Confusion matrix heatmaps + module accuracy comparison chart,
# built from the results dicts produced by metrics.py
# ============================================================

import os
import matplotlib
matplotlib.use("Agg")  # headless-safe; works whether or not a display is present
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def _ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR


def plot_confusion_matrix(module_name: str, result: dict, save: bool = True):
    """Confusion matrix heatmap for one module's evaluation result."""
    cm = result['confusion_matrix']
    labels = result['labels']

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels, ax=ax,
                cbar_kws={'label': 'count'})
    ax.set_title(f"Confusion Matrix — {module_name}\n"
                 f"Accuracy: {result['accuracy']:.2%}  |  "
                 f"F1 (macro): {result['f1']:.2%}",
                 fontweight='bold')
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.tight_layout()

    if save:
        out_dir = _ensure_output_dir()
        safe_name = module_name.lower().replace(' ', '_')
        path = os.path.join(out_dir, f"confusion_matrix_{safe_name}.png")
        plt.savefig(path, dpi=150)
        print(f"  Saved: {path}")
    plt.close(fig)


def plot_module_comparison(results_by_module: dict, save: bool = True):
    """Bar chart comparing Accuracy / Precision / Recall / F1 across
    every evaluated module (including the combined Agent)."""
    modules = list(results_by_module.keys())
    metrics = ['accuracy', 'precision', 'recall', 'f1']
    colors = ['#7aa2f7', '#bb9af7', '#9ece6a', '#e0af68']

    x = np.arange(len(modules))
    width = 0.2

    fig, ax = plt.subplots(figsize=(11, 6))
    for i, (metric, color) in enumerate(zip(metrics, colors)):
        values = [results_by_module[m][metric] for m in modules]
        ax.bar(x + i * width, values, width, label=metric.capitalize(), color=color)

    ax.set_xticks(x + width * (len(metrics) - 1) / 2)
    ax.set_xticklabels(modules, rotation=20, ha='right')
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.set_title("Module Comparison — Accuracy / Precision / Recall / F1 "
                 "(against ground truth)", fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()

    if save:
        out_dir = _ensure_output_dir()
        path = os.path.join(out_dir, "module_comparison.png")
        plt.savefig(path, dpi=150)
        print(f"  Saved: {path}")
    plt.close(fig)


def print_summary_table(results_by_module: dict):
    """Console-friendly summary table of all modules' scores."""
    print(f"\n{'Module':<20} {'Accuracy':>10} {'Precision':>11} {'Recall':>9} {'F1':>8}")
    print("-" * 60)
    for name, r in results_by_module.items():
        print(f"{name:<20} {r['accuracy']:>9.2%} {r['precision']:>10.2%} "
              f"{r['recall']:>8.2%} {r['f1']:>7.2%}")
