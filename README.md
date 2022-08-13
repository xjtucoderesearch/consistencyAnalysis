# consistencyAnalysis

## Extract relations from tool

### Sourcetrail

#### Usage:

1) Build a project and analysis using `Sourcetrail`
2) Run the following step:
```text
python Extract/Format/Sourcetrail.py lang project_name database path_prefix output_path
```
example:
```text
python Extract/Format/Sourcetrail.py cpp bitcoin D:/gitrepo/cpp/bitcoin/bitcoin.srctrldb D:/gitrepo/cpp/bitcoin/ C:/Users/dzf/Desktop
```
3) Result

### Understand

#### Usage:

1) Build a project and analysis using `Understand`
2) Run the following step:
```text
upython Extract/Format/Understand.py lang project_name database output_path
```
example:
```text
upython Extract/Format/Sourcetrail.py cpp bitcoin D:/gitrepo/cpp/bitcoin/bitcoin.srctrldb C:/Users/dzf/Desktop
```
3) Result

### Depends

#### Usage:

1) Run the following step:
```text
java -jar Extract/tools/depends.jar lang project_path project_name -g var
```
example:
```text
java -jar Extract/tools/depends.jar python ./boto3 boto3 -g var
```

### Results Structure

```json
{
  "script_ver": "1.0.0",
  "und_ver": 1083,
  "db_name": "database_name.und",
  "entities": [
    {
      "id": 39,
      "type": "Public Property",
      "name": "ENREContext.scope",
      "line": 5,
      "start_column": 3,
      "end_column": 8,
      "belongs_to": 30
    }
  ],
  "relations": [
    {
      "from": 1,
      "to": 10,
      "type": "web Javascript Define",
      "line": 1,
      "column": 7
    }
  ]
}
```