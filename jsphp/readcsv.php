<?php
$f_path = $_REQUEST["file"];
$file = fopen($f_path,"r");

$header = fgetcsv($file); 
$data = [];
while(!feof($file))
{
  $temp = fgetcsv($file);
  array_push($data, $temp[0], (int) $temp[1]);
}
fclose($file);

echo json_encode($data);

?> 
