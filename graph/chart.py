import matplotlib.pyplot as plt

frameworks = ['Django\nDevServer', 'Django\nGunicorn', 'Django Gunicorn\n--6 workers\n--2 threads', 'FastAPI\nuvicorn']
times = [0, 1.71, 0.35, 0.08]  # Time in seconds for 1,000,000 records

plt.figure(figsize=(12, 8))
plt.bar(frameworks, times, color=['black', 'red', 'blue', 'green'])

plt.title('Comparison of Execution Time on 1,000,000 Records', fontsize=16)
plt.ylabel('Time (seconds)', fontsize=14)
plt.xlabel('Frameworks', fontsize=14)

plt.ylim(0, 2)

plt.subplots_adjust(bottom=0.15)  # Increase this value to shift up

for i in range(len(frameworks)):
    plt.text(i, times[i] + 0.05, str(times[i]), ha='center', fontsize=12)

plt.show()
