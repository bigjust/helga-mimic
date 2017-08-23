helga-mimic
===========

Builds markov chains of users and channels. Will produce an example
line on demand. commands will allow for rebuilding the markov chain
for a channel or user.

Requires the .. _helga-oral-history: https://github.com/bigjust/helga-oral-history

We've also integrated cobe (https://github.com/pteichman/cobe) which
is the latest iteration of MegaHAL, a conversational brain that uses
markov chains for learning and can respond to statements, using the
message as a seed.

Usage
-----

We can mimic the current channel::

  <bigjust> !mimic
  <helga> if not, why are we counting from dusk till dawn?

or a specific user::

  <bigjust> !mimic bigjust
  <helga> I'm a dork, haha

or a list of users::

  <bigjust> !mimic bigjust justin
  <helga> I thought W was the 25th anniversary of the GOP

replace brain by relearning whats in the db (aka how we update
currently)::

  <bigjust> !mimic build
  <helga> I learned some stuff!

 teach helga a new personality::

   <bigjust> !mimic load <key> <url>
   <helga> <key> loaded.
   <bigjust> !mimic <key>
   <helga> wuba dub dub!

License
-------

Copyright (c) 2016 Justin Caratzas

GPLv3 Licensed
