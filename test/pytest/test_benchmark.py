import timeit
import numpy as np
import csv
import NumCppPy as NumCpp
from tqdm import tqdm

# --- Настройки ---
SIZES = [1000, 10000, 100000]  # Размеры массивов для тестов
REPEATS = 5  # Количество повторов для усреднения
NUMBER = 10  # Количество вызовов в каждом замере

# --- Функции для тестирования ---
FUNCTIONS = [
    ("sum", lambda arr: NumCpp.sum(arr)),
    ("mean", lambda arr: NumCpp.mean(arr)),
    ("prod", lambda arr: NumCpp.prod(arr)),
    ("dot", lambda arr: NumCpp.dot(arr, arr)),
]

LINALG_FUNCTIONS = [
    ("det", lambda arr: NumCpp.det(arr)),
    ("inv", lambda arr: NumCpp.inv(arr)),
    ("lstsq", lambda arr: NumCpp.lstsq(arr, arr, 1e-12)),
]

INTEGRATE_FUNCTIONS = [
    ("trapazoidal", lambda poly, a, b: NumCpp.integrate_trapazoidal(poly, a, b)),
    ("simpson", lambda poly, a, b: NumCpp.integrate_simpson(poly, a, b)),
    ("romberg", lambda poly, a, b: NumCpp.integrate_romberg(poly, a, b)),
    ("gauss_legendre", lambda poly, a, b: NumCpp.integrate_gauss_legendre(poly, a, b)),
]

# --- For progress visualization ---
BENCHMARK_PLAN = []
for size in SIZES:
    for fname in ["sum", "mean", "prod", "dot"]:
        BENCHMARK_PLAN.append(("Functions", fname, size))
for size in [10, 50, 100]:
    for fname in ["det", "inv", "lstsq"]:
        BENCHMARK_PLAN.append(("Linalg", fname, size))
for degree in [3, 5, 7]:
    for fname in ["trapazoidal", "simpson", "romberg", "gauss_legendre"]:
        BENCHMARK_PLAN.append(("Integrate", fname, degree))
TOTAL = len(BENCHMARK_PLAN)
progress_counter = [0]  # mutable for nested functions

def print_progress(group, fname, size_or_degree, extra=None):
    progress_counter[0] += 1
    msg = f"[{progress_counter[0]}/{TOTAL}] {group}: {fname}, "
    if group == "Functions" or group == "Linalg":
        msg += f"size={size_or_degree}"
    else:
        msg += f"degree={size_or_degree}"
        if extra:
            msg += f", interval={extra}"
    print(msg, flush=True)

# --- Бенчмарк функций работы с массивами ---
def benchmark_functions():
    results = []
    with tqdm(total=len(SIZES)*4, desc="Functions", ncols=80) as pbar:
        for size in SIZES:
            arr = np.random.rand(size)
            nc_arr = NumCpp.NdArray(arr.shape[0])
            nc_arr.setArray(arr)
            for fname, func in [
                ("sum", lambda a: NumCpp.sum(a, NumCpp.Axis.NONE)),
                ("mean", lambda a: NumCpp.mean(a, NumCpp.Axis.NONE)),
                ("prod", lambda a: NumCpp.prod(a, NumCpp.Axis.NONE)),
                ("dot", lambda a: NumCpp.dot(a, a)),
            ]:
                pbar.set_postfix({"function": fname, "size": size})
                t = min(timeit.repeat(lambda: func(nc_arr), repeat=REPEATS, number=NUMBER))
                results.append({"group": "Functions", "function": fname, "size": size, "time": t / NUMBER})
                pbar.update(1)
    return results

# --- Бенчмарк линейной алгебры ---
def benchmark_linalg():
    results = []
    with tqdm(total=3*3, desc="Linalg", ncols=80) as pbar:
        for size in [5, 8, 10]:
            arr = np.random.rand(size, size)
            nc_arr = NumCpp.NdArray(arr.shape[0], arr.shape[1])
            nc_arr.setArray(arr)
            for fname, func in [
                ("det", lambda a: NumCpp.det(a)),
                ("inv", lambda a: NumCpp.inv(a)),
                ("lstsq", lambda a: NumCpp.lstsq(a, a, 1e-12)),
            ]:
                pbar.set_postfix({"function": fname, "size": size})
                try:
                    t = min(timeit.repeat(lambda: func(nc_arr), repeat=REPEATS, number=NUMBER))
                    results.append({"group": "Linalg", "function": fname, "size": size, "time": t / NUMBER})
                except Exception as e:
                    results.append({"group": "Linalg", "function": fname, "size": size, "time": -1, "error": str(e)})
                pbar.update(1)
    return results

# --- Бенчмарк интегрирования ---
def benchmark_integrate():
    results = []
    with tqdm(total=3*4, desc="Integrate", ncols=80) as pbar:
        for degree in [3, 5, 7]:
            coeffs = np.random.randint(-10, 10, degree)
            nc_coeffs = NumCpp.NdArray(1, degree)
            nc_coeffs.setArray(coeffs)
            poly = NumCpp.Poly1d(nc_coeffs, NumCpp.IsRoots.NO)
            a, b = np.sort(np.random.rand(2) * 100 - 50)
            for fname, func in [
                ("trapazoidal", lambda p, x, y: NumCpp.integrate_trapazoidal(p, x, y)),
                ("simpson", lambda p, x, y: NumCpp.integrate_simpson(p, x, y)),
                ("romberg", lambda p, x, y: NumCpp.integrate_romberg(p, x, y)),
                ("gauss_legendre", lambda p, x, y: NumCpp.integrate_gauss_legendre(p, x, y)),
            ]:
                pbar.set_postfix({"function": fname, "degree": degree, "interval": f"[{a:.2f},{b:.2f}]"})
                try:
                    t = min(timeit.repeat(lambda: func(poly, a, b), repeat=REPEATS, number=NUMBER))
                    results.append({"group": "Integrate", "function": fname, "degree": degree, "interval": f"[{a:.2f},{b:.2f}]", "time": t / NUMBER})
                except Exception as e:
                    results.append({"group": "Integrate", "function": fname, "degree": degree, "interval": f"[{a:.2f},{b:.2f}]", "time": -1, "error": str(e)})
                pbar.update(1)
    return results

# --- Сохранение результатов ---
def save_results(results, filename):
    if not results:
        print("No results to save!")
        return
    # Collect all possible keys
    all_keys = set()
    for row in results:
        all_keys.update(row.keys())
    keys = list(all_keys)
    # Fill missing fields with ''
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in results:
            for k in keys:
                if k not in row:
                    row[k] = ''
            writer.writerow(row)

if __name__ == "__main__":
    all_results = []
    all_results.extend(benchmark_functions())
    all_results.extend(benchmark_linalg())
    all_results.extend(benchmark_integrate())
    print("Benchmark complete. Results saved to benchmark_results.csv")
    save_results(all_results, "benchmark_results.csv") 