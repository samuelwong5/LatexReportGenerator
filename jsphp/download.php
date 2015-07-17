<?php

// Path to save images to
$path = "/home/samuelwong/Report/graphs/";    
$img = urldecode($_POST["s"]);
$name = $_POST["name"];

// Strip headers
$img = str_replace('data:image/png;base64,', '', $img);
$img = str_replace(' ', '+', $img);
$data = base64_decode($img);
$fpath = $path . $name . ".png";
$file = fopen($fpath, "wb") or die(print_r(error_get_last(),true));
$bytes = $bytes . fwrite($file, $data);
fclose($file);

?>
