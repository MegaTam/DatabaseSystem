def optimal_page_replacement(n, m, pages):
    buffer = set()  # initialize a buffer
    # initialize a dictionary to store the positions of each page
    page_pos = {page: [] for page in pages}
    reads_from_disk = 0     # initialize number of reads from disk
    for i in range(n):
        page_pos[pages[i]].append(i)    # store the position of the pages
    # start the readings
    for i in range(n):
        current_page = pages[i]
        # Remove the current page's position (already visited)
        page_pos[current_page].pop(0)
        if current_page not in buffer:
            if len(buffer) < m: # buffer is not full
                buffer.add(current_page)
                reads_from_disk += 1
            else:   # buffer is full
                farthest_use = -1   # initialize the largest
                page_to_evict = None
                # Find the page with the farthest future use or one that is not used again
                for page in buffer:
                    if page_pos[page]:  # the page will be used again
                        next_use = page_pos[page][0]
                    else:   # the page will not be used again
                        next_use = n    # set the next use as a large number
                    if next_use > farthest_use:
                        farthest_use = next_use
                        page_to_evict = page    # get the
                # update the buffer
                buffer.remove(page_to_evict)
                buffer.add(current_page)
                reads_from_disk += 1
        # The current page is already in the buffer
        else:
            continue
    return reads_from_disk


line_1 = input().split()
n = int(line_1[0])
m = int(line_1[1])
line_2 = input()
pages = line_2.split()
print(optimal_page_replacement(n, m, pages))
