<?php
$f_path = $_REQUEST["file"];
$data_path = "/home/samuelwong/Report/HKSWROutput/report/";
$file = fopen($data_path . $f_path,"r");
if(!$file) die("[ERROR] File not found.");
$data = array();
$header = fgetcsv($file);
array_push($data, array($header[0], $header[1]));
while(!feof($file))
{
  $temp = fgetcsv($file);
  array_push($data, array($temp[0], (int) $temp[1]));
}
echo json_encode($data);
?>
