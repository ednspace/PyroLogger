#!/usr/bin/perl -w
use strict;

my $offset = 0.0;
while(1) {
    print sin($offset)."\n";
    $offset += 0.1;
    if ($offset > 500) {
	last;
    }
    system("sleep 1") == 0
	or last;
}


