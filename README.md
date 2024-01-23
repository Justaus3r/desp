# desp
diff generator for Bahria University Exam Seatings(highly specific ,mostly for personal use + frenqs)

# But Why?
Why not!. Also studying is for boomers...


# Dowloads
**Note: before downloading , please read the [Note](https://github.com/Justaus3r/desp#Note)**<br>
binary built using [nuitka](https://github.com/Nuitka/Nuitka) and packaged using [innosetup](https://jrsoftware.org/isinfo.php).

download from [here](https://github.com/Justaus3r/desp/releases/download/v0.1.0/desp-0.1.0_amd64.exe)


# I want it to work for me:
Change the indices in [```HarvestIndices```](https://github.com/Justaus3r/desp/blob/master/desp/parse_exam_pdf.py#L8) class to match the fetch points of your pdf. OR just change the horrible implementation of [``get_parsed_data()``](https://github.com/Justaus3r/desp/blob/master/desp/parse_exam_pdf.py#L30) to a generic one that doesn't break all the times(please fork and do that + send a PR)

# Note:
This is just a poc, will break in most cases.

Working Probability: 69%. Well,  because its dumb and assumes that all pdfs are identical with 10 rows. Though it does perform a single iteration filtering to remove a single diff to match with base-case. It uses embedded indices to harvest all the required data(hence called harvest indices), so it probably won't work for Different Departments OR
Semesters **(Though , might be made to work by changing the harvest indices)**.

A Better way might be to parse the pdf and use regex to match patterns and harvest data. The fix is not that hard, just requires a rewrite of get_parsed_data() keeping its signature same, But i am not motivated enough to do that


# License
Licensed Under GPLV3 and later.
