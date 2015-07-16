<?php

$img = $_REQUEST["s"];
$name = $_REQUEST["name"];
echo($img);
echo($name);
$img = str_replace('data:image/png;base64,', '', $img);
$img = str_replace(' ', '+', $img);
$data = base64_decode($img);
$file = fopen($name . ".png", "wb") or die("Unable to open file!");
echo($name . ".png");
fwrite($file, $data);
fclose($file);

?>
