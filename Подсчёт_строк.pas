uses System.IO;

//    var folder := Directory.GetDirectories(Directory.GetCurrentDirectory, '*');  //GetFiles('C:\PABCWork.NET\programms\4 курс\Дз на каникулы', '*.pas');  

var global_counter: integer;

function count_lines_in_file(FilePath: string): integer;
  var 
    f: text;
    noused: string; // Для Read()
begin
  assign(f, FilePath);
  reset(f);
  var res:= 0;
  
  while not f.Eof do
  begin
    res += 1;
    Readln(f, noused);
  end;
  close(f);
  result:= res;
end;

procedure да_сколько_там_этих_папок(current_path: string);
begin
  var folders:= Directory.GetDirectories(current_path, '*');
  foreach var folder in folders do
    if ExtractFileName(folder) not in ['__pycache__', '.venv', '.idea', '.git'] then 
      да_сколько_там_этих_папок(current_path + '\' + ExtractFileName(folder));
  
  var files:= Directory.GetFiles(current_path);
  foreach var filePath in files do
    if ExtractFileName(filePath) not in ['.DS_Store', '.env', '.gitignore', 'README.md', 'requirements.txt', 'tasklist.md'] then
    global_counter+= count_lines_in_file(filePath);
end;

begin  
  да_сколько_там_этих_папок(Directory.GetCurrentDirectory);
  Writeln(global_counter - count_lines_in_file('Подсчёт_строк.pas'));
end.  