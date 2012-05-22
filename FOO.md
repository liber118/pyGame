Multitool - Command Line Reference
==================================
    multitool [param] [param] ...

First tap must be a <code>source</code> and last tap must be a <code>sink</code>

<table>
<tr><th>options:</th></tr>
<tr><td><code>-h|--help</code></td><td>show this help text</td></tr>
<tr><td><code>--markdown</code></td><td>generate help text as GitHub Flavored Markdown</td></tr>
<tr><td><code>--dot=filename</code></td><td>write a plan DOT file, then exit</td></tr>
<tr><th>taps:</th></tr>
<tr><td><code>source</code></td><td>an url to input data</td></tr>
<tr><td><code>source.name</code></td><td>name of this source, required if more than one</td></tr>
<tr><td><code>source.skipheader</code></td><td>set true if the first line should be skipped</td></tr>
<tr><td><code>source.hasheader</code></td><td>set true if the first line should be used for field names</td></tr>
<tr><td><code>source.delim</code></td><td>delimiter used to separate fields</td></tr>
<tr><td><code>source.seqfile</code></td><td>read from a sequence file instead of text; specify N fields, or 'true'</td></tr>
<tr><td><code>sink</code></td><td>an url to output path</td></tr>
<tr><td><code>sink.select</code></td><td>fields to sink</td></tr>
<tr><td><code>sink.replace</code></td><td>set true if output should be overwritten</td></tr>
<tr><td><code>sink.compress</code></td><td>compression: enable, disable, or default</td></tr>
<tr><td><code>sink.writeheader</code></td><td>set true to write field names as the first line</td></tr>
<tr><td><code>sink.delim</code></td><td>delimiter used to separate fields</td></tr>
<tr><td><code>sink.seqfile</code></td><td>write to a sequence file instead of text; writeheader, delim, and compress are ignored</td></tr>
<tr><th>operations:</th></tr>
<tr><td><code>reject</code></td><td>regex, matches are discarded. all fields are matched unless args is specified</td></tr>
<tr><td><code>reject.args</code></td><td>fields to match against</td></tr>
<tr><td><code>select</code></td><td>regex, matches are kept. matches against all fields unless args is given</td></tr>
<tr><td><code>select.args</code></td><td>fields to match against</td></tr>
<tr><td><code>cut</code></td><td>split the first field, and return the given fields, or all fields. 0 for first, -1 for last</td></tr>
<tr><td><code>cut.delim</code></td><td>regex delimiter, defaut: '\t' (TAB)</td></tr>
<tr><td><code>parse</code></td><td>parse the first field with given regex</td></tr>
<tr><td><code>parse.groups</code></td><td>regex groups, comma delimited</td></tr>
<tr><td><code>retain</code></td><td>narrow the stream to the given fields. 0 for first, -1 for last</td></tr>
<tr><td><code>discard</code></td><td>narrow the stream removing the given fields. 0 for first, -1 for last</td></tr>
<tr><td><code>pgen</code></td><td>parse the first field with given regex, return as new tuples</td></tr>
<tr><td><code>replace</code></td><td>apply replace the regex</td></tr>
<tr><td><code>replace.replace</code></td><td>replacement string</td></tr>
<tr><td><code>replace.replaceAll</code></td><td>true if pattern should be applied more than once</td></tr>
<tr><td><code>group</code></td><td>what fields to group/sort on, grouped fields are sorted</td></tr>
<tr><td><code>group.secondary</code></td><td>fields to secondary sort on</td></tr>
<tr><td><code>group.secondary.reverse</code></td><td>set true to reverse secondary sort</td></tr>
<tr><td><code>join</code></td><td>what fields to join and group on, grouped fields are sorted</td></tr>
<tr><td><code>join.lhs</code></td><td>source name of the lhs of the join</td></tr>
<tr><td><code>join.lhs.group</code></td><td>lhs fields to group on, default FIRST</td></tr>
<tr><td><code>join.rhs</code></td><td>source name of the rhs of the join</td></tr>
<tr><td><code>join.rhs.group</code></td><td>rhs fields to group on, default FIRST</td></tr>
<tr><td><code>join.joiner</code></td><td>join type: inner, outer, left, right</td></tr>
<tr><td><code>join.name</code></td><td>branch name</td></tr>
<tr><td><code>concat</code></td><td>join the given fields, will join ALL by default</td></tr>
<tr><td><code>concat.delim</code></td><td>delimiter, defaut: '\t' (TAB)</td></tr>
<tr><td><code>gen</code></td><td>split the first field, and return the given result fields as new tuples</td></tr>
<tr><td><code>gen.delim</code></td><td>regex delimiter, defaut: '\t' (TAB)</td></tr>
<tr><td><code>count</code></td><td>count the number of values in the grouping</td></tr>
<tr><td><code>sum</code></td><td>sum the values in the grouping</td></tr>
<tr><td><code>expr</code></td><td>use java expression as function, e.g. $0.toLowerCase()</td></tr>
<tr><td><code>expr.args</code></td><td>the fields to use as arguments</td></tr>
<tr><td><code>sexpr</code></td><td>use java expression as filter, e.g. $0 != null</td></tr>
<tr><td><code>sexpr.args</code></td><td>the fields to use as arguments</td></tr>
<tr><td><code>debug</code></td><td>print tuples to stdout of task jvm</td></tr>
<tr><td><code>debug.prefix</code></td><td>a value to distinguish which branch debug output is coming from</td></tr>
<tr><td><code>filename</code></td><td>include the filename from which the current value was found</td></tr>
<tr><td><code>filename.append</code></td><td>append the filename to the record</td></tr>
<tr><td><code>filename.only</code></td><td>only return the filename</td></tr>
<tr><td><code>unique</code></td><td>return the first value in each grouping</td></tr>
</table>

Using Cascading 2.0.0wip-301

This release is licensed under the Apache Software License 2.0.
