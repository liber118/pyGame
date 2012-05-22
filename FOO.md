multitool [param] [param] ...

Usage:
<table>
<tr><th>options:</th></tr>
<tr><td>-h|--help</td><td>show this help text</td></tr>
<tr><td>--markdown</td><td>generate help text as GitHub Flavored Markdown</td></tr>
<tr><td>--dot=<file></td><td>filename to write a plan DOT file then exit</td></tr>
<tr><th>taps:</th></tr>
<tr><td>source</td><td>an url to input data</td></tr>
<tr><td>source.name</td><td>name of this source, required if more than one</td></tr>
<tr><td>source.skipheader</td><td>set true if the first line should be skipped</td></tr>
<tr><td>source.hasheader</td><td>set true if the first line should be used for field names</td></tr>
<tr><td>source.delim</td><td>delimiter used to separate fields</td></tr>
<tr><td>source.seqfile</td><td>read from a sequence file instead of text; specify N fields, or 'true'</td></tr>
<tr><td>sink</td><td>an url to output path</td></tr>
<tr><td>sink.select</td><td>fields to sink</td></tr>
<tr><td>sink.replace</td><td>set true if output should be overwritten</td></tr>
<tr><td>sink.compress</td><td>compression: enable, disable, or default</td></tr>
<tr><td>sink.writeheader</td><td>set true to write field names as the first line</td></tr>
<tr><td>sink.delim</td><td>delimiter used to separate fields</td></tr>
<tr><td>sink.seqfile</td><td>write to a sequence file instead of text; writeheader, delim, and compress are ignored</td></tr>
<tr><th>operations:</th></tr>
<tr><td>reject</td><td>regex, matches are discarded. all fields are matched unless args is specified</td></tr>
<tr><td>reject.args</td><td>fields to match against</td></tr>
<tr><td>select</td><td>regex, matches are kept. matches against all fields unless args is given</td></tr>
<tr><td>select.args</td><td>fields to match against</td></tr>
<tr><td>cut</td><td>split the first field, and return the given fields, or all fields. 0 for first, -1 for last</td></tr>
<tr><td>cut.delim</td><td>regex delimiter, defaut: '\t' (TAB)</td></tr>
<tr><td>parse</td><td>parse the first field with given regex</td></tr>
<tr><td>parse.groups</td><td>regex groups, comma delimited</td></tr>
<tr><td>retain</td><td>narrow the stream to the given fields. 0 for first, -1 for last</td></tr>
<tr><td>discard</td><td>narrow the stream removing the given fields. 0 for first, -1 for last</td></tr>
<tr><td>pgen</td><td>parse the first field with given regex, return as new tuples</td></tr>
<tr><td>replace</td><td>apply replace the regex</td></tr>
<tr><td>replace.replace</td><td>replacement string</td></tr>
<tr><td>replace.replaceAll</td><td>true if pattern should be applied more than once</td></tr>
<tr><td>group</td><td>what fields to group/sort on, grouped fields are sorted</td></tr>
<tr><td>group.secondary</td><td>fields to secondary sort on</td></tr>
<tr><td>group.secondary.reverse</td><td>set true to reverse secondary sort</td></tr>
<tr><td>join</td><td>what fields to join and group on, grouped fields are sorted</td></tr>
<tr><td>join.lhs</td><td>source name of the lhs of the join</td></tr>
<tr><td>join.lhs.group</td><td>lhs fields to group on, default FIRST</td></tr>
<tr><td>join.rhs</td><td>source name of the rhs of the join</td></tr>
<tr><td>join.rhs.group</td><td>rhs fields to group on, default FIRST</td></tr>
<tr><td>join.joiner</td><td>join type: inner, outer, left, right</td></tr>
<tr><td>join.name</td><td>branch name</td></tr>
<tr><td>concat</td><td>join the given fields, will join ALL by default</td></tr>
<tr><td>concat.delim</td><td>delimiter, defaut: '\t' (TAB)</td></tr>
<tr><td>gen</td><td>split the first field, and return the given result fields as new tuples</td></tr>
<tr><td>gen.delim</td><td>regex delimiter, defaut: '\t' (TAB)</td></tr>
<tr><td>count</td><td>count the number of values in the grouping</td></tr>
<tr><td>sum</td><td>sum the values in the grouping</td></tr>
<tr><td>expr</td><td>use java expression as function, e.g. $0.toLowerCase()</td></tr>
<tr><td>expr.args</td><td>the fields to use as arguments</td></tr>
<tr><td>sexpr</td><td>use java expression as filter, e.g. $0 != null</td></tr>
<tr><td>sexpr.args</td><td>the fields to use as arguments</td></tr>
<tr><td>debug</td><td>print tuples to stdout of task jvm</td></tr>
<tr><td>debug.prefix</td><td>a value to distinguish which branch debug output is coming from</td></tr>
<tr><td>filename</td><td>include the filename from which the current value was found</td></tr>
<tr><td>filename.append</td><td>append the filename to the record</td></tr>
<tr><td>filename.only</td><td>only return the filename</td></tr>
<tr><td>unique</td><td>return the first value in each grouping</td></tr>
</table>

Using Cascading 2.0.0wip-301
This release is licensed under the Apache Software License 2.0.
