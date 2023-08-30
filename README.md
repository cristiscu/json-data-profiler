JSON Data Profiler
==================

Extracts metadata information from any JSON data files.

**Features**

* Shows only single top object in homogenous collections, with optional properties. Use this option when you assume all array objects have the same type, with some properties not always required.
* Shows different types of objects in heterogenous collections, with no optional properties. Use this option when you may have objects of different types in your arrays, and each object type has the same manatory properties.
* Adds an asteryx prefix (*) to the names of optional (i.e. not always required) properties.
* Shows JSON data type for each basic property (numeric, string, bool, null).
* Shows how many times each property appeared in the data file. This is how many objects used that property.
* Show how many distinct values each basic property had.
* Shows the first few values (by defaut three) for each basic property.
* Truncates large text values.
* Shows objects with one single property, and arrays with primive values, on one single line.

**Phase One: Assuming Homogenous Collections**

For the **om.json** input data file, we can first assume that most if not all objects in an array have the same type. For instance, we do not mix customers with orders. The following output files tells us which properties do not appear in all array objects:

```
[
    {
       "*objectDomain": "string", 
       "*objectId": "number", 
       "*objectName": "string", 
       "*stageKind": "string", 
       "*locations": [ "string" ],
       "*columns": 
       [
          {
             "columnId": "number", 
             "columnName": "string"
          }
       ]
    }
]
```

**Phase Two: Adding More Profiling Data**

On the same data structure as before, we added how many objects used a property, how many distinct values we had for each property, what are the first few values for each property:

```
[
    {
       "*objectDomain (114)": "string (2): Stage, Table", 
       "*objectId (114)": "number (11): 1, 62469, 61443, ...", 
       "*objectName (114)": "string (6): WORKSHEETS_APP.PUBLI..., DB1.PUBLIC.CUSTOMERS, DB1.PUBLIC.T1, ...", 
       "*stageKind (104)": "string (1): Internal Named", 
       "*locations (38)": [ "string (1): /" ],
       "*columns (10)": 
       [
          {
             "columnId (2)": "number (2): 63490, 62468", 
             "columnName (2)": "string (2): CITY, NAME"
          }
       ]
    }
]
```

**Phase Three: Assuming Heterogenous Collections**

When you had plenty of optional properties in phase one, you may assume that the collections are not as homogenous, and you can get a better different view, in which each object type is always defined by the exact same set of mandatory properties:

```
[
   {
      "objectDomain (104)": "string (1): Stage", 
      "objectId (104)": "number (1): 1", 
      "objectName (104)": "string (1): WORKSHEETS_APP.PUBLI...", 
      "stageKind (104)": "string (1): Internal Named"
   },
   { "locations (38)": [ "string (1): /" ] },
   {
      "columns (10)": [{
         "columnId (2)": "number (2): 63490, 62468", 
         "columnName (2)": "string (2): CITY, NAME"
      }],
      "objectDomain (10)": "string (1): Table", 
      "objectId (10)": "number (10): 62469, 61443, 62467, ...", 
      "objectName (10)": "string (5): DB1.PUBLIC.CUSTOMERS, DB1.PUBLIC.T1, DB1.PUBLIC.CITIES, ..."
   }
]
```
