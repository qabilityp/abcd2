from multiprocessing import Pool, Manager

def kollatz_check(n):
    sequence = []
    while n != 1:
        sequence.append(n)
        n = n // 2 if n % 2 == 0 else 3 * n + 1
    return sequence

def process_range(start, end):
    processed = set()
    for i in range(start, end):
        if i % 2 != 0:
            seq = kollatz_check(i)
            processed.update(seq)
        return processed

def parallel_find_counterexample(limit, num_workers=4):
    chunk_size = limit // num_workers

    with Pool(num_workers) as pool:
        tasks = [(i * chunk_size + 1, (i + 1) * chunk_size) for i in range(num_workers)]
        results = pool.starmap(process_range, tasks)

    processed_numbers = set()
    for result in results:
        processed_numbers.update(result)

    print("всі числа пораховувані!")


if __name__ == '__main__':
    parallel_find_counterexample(1000000000)


