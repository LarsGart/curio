# import re
# import arxiv

# client = arxiv.Client()
# search = arxiv.Search(
#         query="KAN",
#         max_results=20,
#         sort_by=arxiv.SortCriterion.SubmittedDate
#     )
# results = list(client.results(search))
# for p in results:
#     print('===========')
#     print(p.comment, p.summary)
#     print('LINKS:')
#     for l in p.links:
#         print(l)

# # string = '''This work has been submitted to IEEE for possible publication.
# #   Copyright may be transferred without notice, after which this version may no
# #   longer be accessible. Related Code: https://gitasdasdhub.com/ezeydan/F-KANs.git https://giasasasdthub.com/ezeydan/F-KANs.git'''

# # links =  re.findall(r'(https?://github.com/[^ ]+)', string)
# # # truncate links to only the first one found if any
# # if len(links) > 0:
# #     links = links[0]
# # print(links)
s = r'''asdsdd%as'''
s.strip(r'%')
print(s)
if '%' in s:
    s = s[:s.find('%')]
    print(s)