# Reinforcement Learning: An Introduction

## node1.html

Contents
Next: Preface
Up: Book
Previous: Book
Contents
I. The Problem
1. Introduction
2. Evaluative Feedback
3. The Reinforcement Learning Problem
II. Elementary Solution Methods
4. Dynamic Programming
5. Monte Carlo Methods
6. Temporal-Difference Learning
III. A Unified View
7. Eligibility Traces
8. Generalization and Function Approximation
9. Planning and Learning
10. Dimensions of Reinforcement Learning
11. Case Studies
Bibliography
Subsections
Preface
Series Forward
Summary of Notation
Mark Lee
2005-01-04

## node2.html

Preface
Next: Series Forward
Up: Contents
Previous: Contents
Contents
Preface
We first came to focus on what is now known as reinforcement learning in late
1979.
We were both at the University of Massachusetts, working on one of the
earliest projects to revive the idea that networks of neuronlike adaptive
elements might prove to be a promising approach to artificial adaptive
intelligence. The project explored the "heterostatic theory of adaptive systems"
developed by A. Harry Klopf. Harry's work was a rich source of ideas, and we were
permitted to explore them critically and compare them with the long history of
prior work in adaptive systems.
Our task became one of teasing the ideas apart
and understanding their relationships and relative importance.
This
continues today, but in 1979 we came to realize that perhaps the simplest of
the ideas, which had long been taken for granted, had received surprisingly
little attention from a computational perspective. This was simply the idea of a
learning system that wants something, that adapts its behavior in order to
maximize a special signal from its environment. This was the idea of a
"hedonistic" learning system, or, as we would say now, the idea of reinforcement
learning.
Like others, we had a sense that reinforcement learning had been thoroughly
explored in the early days of cybernetics and artificial intelligence. On closer
inspection, though, we found that it had been explored only slightly. While
reinforcement learning had clearly motivated some of the earliest computational
studies of learning, most of these researchers
had gone on to other things, such as pattern classification, supervised learning,
and adaptive control, or they had
abandoned the study of learning altogether. As a
result, the special issues involved in learning how to get something from the
environment received relatively little attention. In retrospect, focusing on this
idea was the critical step that set this branch of research in motion.
Little
progress could be made in the computational study of reinforcement learning until
it was recognized that such a fundamental idea had not yet been thoroughly
explored.
The field has come a long way since then, evolving and maturing in several
directions.
Reinforcement learning has gradually become one of the most active
research areas in machine learning, artificial intelligence, and neural network
research. The field has developed strong mathematical foundations and impressive
applications.
The computational study of
reinforcement learning is now a large field, with hundreds of active researchers
around the world in diverse disciplines such as psychology, control theory,
artificial intelligence, and neuroscience. Particularly important have been the
contributions establishing and developing the relationships to the theory of
optimal control and dynamic programming.
The overall problem of learning from
interaction to achieve goals is still far from being solved, but our understanding
of it has improved significantly.
We can now place component ideas, such as
temporal-difference learning, dynamic programming, and function approximation,
within a coherent perspective with respect to the overall problem.
Our goal in writing this book was to provide a clear and simple account of the key
ideas and algorithms of reinforcement learning. We wanted our treatment to be
accessible to readers in all of the related disciplines, but we could not cover
all of these perspectives in detail. Our treatment takes almost exclusively the
point of view of artificial intelligence and engineering,
leaving coverage of connections to psychology, neuroscience, and other fields to
others or to another time. We also chose not to produce a rigorous formal
treatment of reinforcement learning. We did not reach for the highest possible
level of mathematical abstraction and did not rely on a theorem-proof format.
We
tried to choose a level of mathematical detail that points the mathematically
inclined in the right directions without distracting from the simplicity and
potential generality of the underlying ideas.
The book consists of three parts.
Part I is introductory and problem
oriented.
We focus on the simplest aspects of reinforcement learning
and on its main distinguishing features. One full chapter is devoted to introducing
the reinforcement learning problem whose solution we explore in the rest of
the book. Part II presents what we see as the three most important elementary
solution methods: dynamic programming, simple Monte Carlo methods, and
temporal-difference learning. The first of these is a planning method and assumes
explicit knowledge of all aspects of a problem, whereas the other two are learning
methods.
Part III is concerned with generalizing these methods and blending
them.
Eligibility traces allow unification of Monte Carlo and temporal-difference
methods, and function approximation methods such as artificial neural networks extend
all the methods so that they can be applied to much larger problems.
We bring
planning and learning methods together again and relate them to heuristic search.
Finally, we summarize our view of the state of reinforcement learning research
and briefly present case studies, including some of the most
impressive applications of reinforcement learning to date.
This book was designed to be used as a text in a one-semester course, perhaps
supplemented by readings from the literature or by a more mathematical text such
as the excellent one by Bertsekas and Tsitsiklis (1996).
This book can also be
used as part of a broader course on machine learning, artificial intelligence,
or neural networks. In this case, it may be desirable to cover only a subset of
the material.
We recommend covering Chapter 1 for a brief overview, Chapter 2
through Section 2.2, Chapter 3 except Sections 3.4, 3.5 and 3.9, and then
selecting sections from the remaining chapters according to time and interests.
Chapters 4, 5, and 6 build on each other and are best covered in sequence; of
these, Chapter 6 is the most important for the subject and for the rest of the
book.
A course focusing on machine learning or neural networks should cover
Chapter 8, and a course focusing on artificial intelligence or planning should
cover Chapter 9.
Chapter 10 should almost always be covered because it is
short and summarizes the overall unified view of reinforcement learning methods
developed in the book.
Throughout the book, sections that are more difficult and
not essential to the rest of the book are marked with a
.
These can be omitted on first reading without creating problems later on.
Some exercises are marked with a
to indicate that they are more advanced and not essential to understanding the
basic material of the chapter.
The book is largely self-contained.
The only mathematical background assumed is
familiarity with elementary concepts of probability,
such as expectations of random variables. Chapter 8 is substantially easier to
digest if the reader has some knowledge of artificial neural networks
or some other kind of supervised learning method, but it can be read without
prior background.
We strongly recommend working the exercises provided throughout
the book.
Solution manuals are available to instructors.
This and other related
and timely material is available via the Internet.
At the end of most chapters is a section entitled "Bibliographical and Historical
Remarks," wherein we credit the sources of the ideas presented in that chapter,
provide pointers to further reading and ongoing research, and describe relevant
historical background. Despite our attempts to make these sections authoritative
and complete, we have undoubtedly left out some important prior work.
For that we
apologize, and welcome corrections and extensions for incorporation into a
subsequent edition.
In some sense we have been working toward this book for twenty years, and we have
lots of people to thank.
First, we thank those who have personally helped us
develop the overall view presented in this book: Harry Klopf, for helping us
recognize that reinforcement learning needed to be revived; Chris Watkins,
Dimitri Bertsekas, John Tsitsiklis, and Paul Werbos, for helping us see the value
of the relationships to dynamic programming; John Moore and Jim Kehoe, for insights
and inspirations from animal learning theory; Oliver Selfridge, for emphasizing the
breadth and importance of adaptation; and, more generally, our colleagues and
students who have contributed in countless ways: Ron Williams, Charles Anderson,
Satinder Singh, Sridhar Mahadevan, Steve Bradtke, Bob Crites, Peter Dayan, and
Leemon Baird.
Our view of reinforcement learning has been significantly enriched
by discussions with Paul Cohen, Paul Utgoff, Martha Steenstrup, Gerry Tesauro, Mike
Jordan, Leslie Kaelbling, Andrew Moore, Chris Atkeson, Tom Mitchell, Nils Nilsson,
Stuart Russell, Tom Dietterich, Tom Dean, and Bob Narendra.
We thank Michael
Littman, Gerry Tesauro, Bob Crites, Satinder Singh, and Wei Zhang for providing
specifics of Sections 4.7, 11.1, 11.4, 11.5, and 11.6 respectively.
We thank the
the Air Force Office of Scientific Research, the National Science Foundation, and
GTE Laboratories for their long and farsighted support.
We also wish to thank the many people who have read drafts of
this book and provided valuable comments, including
Tom Kalt,
John Tsitsiklis,
Pawel Cichosz,
Olle Gällmo,
Chuck Anderson,
Stuart Russell,
Ben Van Roy,
Paul Steenstrup,
Paul Cohen,
Sridhar Mahadevan,
Jette Randlov,
Brian Sheppard,
Thomas O'Connell,
Richard Coggins,
Cristina Versino,
John H. Hiett,
Andreas Badelt,
Jay Ponte,
Joe Beck,
Justus Piater,
Martha Steenstrup,
Satinder Singh,
Tommi Jaakkola,
Dimitri Bertsekas,
Torbjörn Ekman,
Christina Björkman,
Jakob Carlström,
and Olle Palmgren.
Finally,
we thank Gwyn Mitchell for helping in many ways, and Harry Stanton and Bob Prior
for being our champions at MIT Press.
Next: Series Forward
Up: Contents
Previous: Contents
Contents
Mark Lee
2005-01-04

## node3.html

Series Forward
Next: Summary of Notation
Up: Contents
Previous: Preface
Contents
Series Forward
I am pleased to have this book by Richard Sutton and Andrew Barto as one of the first
books in the new Adaptive Computation and Machine Learning series. This textbook
presents a comprehensive introduction to the exciting field of reinforcement learning.
Written by two of the pioneers in this field, it provides students, practitioners, and
researchers with an intuitive understanding of the central concepts of reinforcement
learning as well as a precise presentation of the underlying mathematics. The book
also communicates the excitement of recent practical applications of reinforcement
learning and the relationship of reinforcement learning to the core questions in artifical
intelligence. Reinforcement learning promises to be an extremely important new
technology with immense practical impact and important scientific insights into the
organization of intelligent systems.
The goal of building systems that can adapt to their environments and learn from
their experience has attracted researchers from many fields, including computer science,
engineering, mathematics, physics, neuroscience, and cognitive science. Out
of this research has come a wide variety of learning techniques that have the potential
to transform many industrial and scientific fields. Recently, several research
communities have begun to converge on a common set of issues surrounding supervised,
unsupervised, and reinforcement learning problems. The MIT Press series
on Adaptive Computation and Machine Learning seeks to unify the many diverse
strands of machine learning research and to foster high quality research and innovative
applications.
Thomas Diettrich
Next: Summary of Notation
Up: Contents
Previous: Preface
Contents
Mark Lee
2005-01-04

