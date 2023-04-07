<?php
exec("make -C ..", $output);
readfile("index.html");
?><hr><pre>
<?php foreach($output as $line) print($line . "\n"); ?>
</pre>