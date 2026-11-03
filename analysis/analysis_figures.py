from analysis.fig1_runPath import plot_fig1
from analysis.fig2_runWindRMS import plot_fig2
from analysis.fig3_runMassRMS import plot_fig3

def main():
    pdf_path_1 = plot_fig1(report=True)
    pdf_path_2 = plot_fig2(report=True)
    pdf_path_3 = plot_fig3(report=True)

    print(f"[V] Plots successfully saved as pdf files to:")
    print(f"  - {pdf_path_1}")
    print(f"  - {pdf_path_2}")
    print(f"  - {pdf_path_3}")

if __name__ == "__main__":
    main()