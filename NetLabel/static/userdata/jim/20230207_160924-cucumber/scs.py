

tags = []
with open(f'classes.txt', 'r') as f:
    for text in f.read().split('\n'):
        print(text)
        # if text != "\n":
        #     tags.append(text)
# print(tags)