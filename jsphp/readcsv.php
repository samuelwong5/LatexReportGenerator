<?php
echo "hello world";
$f_path = $_REQUEST["file"];
$file = fopen($f_path,"r");
echo "Opening file";
if($file) die("File not found.");
$header = fgetcsv($file); 
$data = [];
while(!feof($file))
{
  $temp = fgetcsv($file);
  //echo $temp;
  array_push($data, $temp[0], (int) $temp[1]);
}
fclose($file);

echo "hello";
//echo $data;

?> 
