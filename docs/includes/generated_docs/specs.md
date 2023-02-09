## 1 Filtering an event frame


### 1.1 Including rows


#### 1.1.1 Take with column

This example makes use of an event-level table named `e` containing the following data:

| patient|i1|b1 |
| - | - | - |
| 1|101|T |
| 1|102|T |
| 1|103| |
| 2|201|T |
| 2|202| |
| 2|203|F |
| 3|301| |
| 3|302|F |

```
e.take(e.b1).i1.sum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|203 |
| 2|201 |
| 3| |



#### 1.1.2 Take with expr

This example makes use of an event-level table named `e` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|111 |
| 1|102|112 |
| 1|103|113 |
| 2|201|211 |
| 2|202|212 |
| 2|203|213 |
| 3|301| |

```
e.take((e.i1 + e.i2) < 413).i1.sum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|306 |
| 2|201 |
| 3| |



#### 1.1.3 Take with constant true

This example makes use of an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 1|102 |
| 2|201 |

```
e.take(True).count_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|2 |
| 2|1 |



#### 1.1.4 Take with constant false

This example makes use of an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 1|102 |
| 2|201 |

```
e.take(False).count_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|0 |
| 2|0 |



#### 1.1.5 Chain multiple takes

This example makes use of an event-level table named `e` containing the following data:

| patient|i1|b1 |
| - | - | - |
| 1|1|T |
| 1|2|T |
| 1|3|F |

```
e.take(e.i1 >= 2).take(e.b1).i1.sum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|2 |



### 1.2 Excluding rows


#### 1.2.1 Drop with column

This example makes use of an event-level table named `e` containing the following data:

| patient|i1|b1 |
| - | - | - |
| 1|101|T |
| 1|102|T |
| 1|103| |
| 2|201|T |
| 2|202| |
| 2|203|F |
| 3|301|T |
| 3|302|T |

```
e.drop(e.b1).i1.sum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|103 |
| 2|405 |
| 3| |



#### 1.2.2 Drop with expr

This example makes use of an event-level table named `e` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|111 |
| 1|102|112 |
| 1|103|113 |
| 2|201|211 |
| 2|202|212 |
| 2|203|213 |
| 3|301| |

```
e.drop((e.i1 + e.i2) < 413).i1.sum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1| |
| 2|405 |
| 3|301 |



#### 1.2.3 Drop with constant true

This example makes use of an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 1|102 |
| 2|201 |

```
e.drop(True).count_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|0 |
| 2|0 |



#### 1.2.4 Drop with constant false

This example makes use of an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 1|102 |
| 2|201 |

```
e.drop(False).count_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|2 |
| 2|1 |



## 2 Picking one row for each patient from an event frame


### 2.1 Picking the first or last row for each patient


#### 2.1.1 Sort by column pick first

This example makes use of an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 1|102 |
| 1|103 |
| 2|203 |
| 2|202 |
| 2|201 |

```
e.sort_by(e.i1).first_for_patient().i1
```
returns the following patient series:

| patient | value |
| - | - |
| 1|101 |
| 2|201 |



#### 2.1.2 Sort by column pick last

This example makes use of an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 1|102 |
| 1|103 |
| 2|203 |
| 2|202 |
| 2|201 |

```
e.sort_by(e.i1).last_for_patient().i1
```
returns the following patient series:

| patient | value |
| - | - |
| 1|103 |
| 2|203 |



### 2.2 Sort by more than one column and pick the first or last row for each patient


#### 2.2.1 Sort by multiple columns pick first

This example makes use of an event-level table named `e` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|3 |
| 1|102|2 |
| 1|102|1 |
| 2|203|1 |
| 2|202|2 |
| 2|202|3 |

```
e.sort_by(e.i1, e.i2).first_for_patient().i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|3 |
| 2|2 |



#### 2.2.2 Sort by multiple columns pick last

This example makes use of an event-level table named `e` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|3 |
| 1|102|2 |
| 1|102|1 |
| 2|203|1 |
| 2|202|2 |
| 2|202|3 |

```
e.sort_by(e.i1, e.i2).last_for_patient().i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|2 |
| 2|1 |



### 2.3 Picking the first or last row for each patient where a column contains NULLs


#### 2.3.1 Sort by column with nulls and pick first

This example makes use of an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1| |
| 1|102 |
| 1|103 |
| 2|203 |
| 2|202 |
| 2| |

```
e.sort_by(e.i1).first_for_patient().i1
```
returns the following patient series:

| patient | value |
| - | - |
| 1| |
| 2| |



#### 2.3.2 Sort by column with nulls and pick last

This example makes use of an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1| |
| 1|102 |
| 1|103 |
| 2|203 |
| 2|202 |
| 2| |

```
e.sort_by(e.i1).last_for_patient().i1
```
returns the following patient series:

| patient | value |
| - | - |
| 1|103 |
| 2|203 |



## 3 Aggregating event and patient frames


### 3.1 Determining whether a row exists for each patient


#### 3.1.1 Exists for patient on event frame

This example makes use of a patient-level table named `p` and an event-level table named `e` containing the following data:

| patient|b1 |
| - | - |
| 1| |
| 2| |
| 3| |

| patient|b1 |
| - | - |
| 1| |
| 1| |
| 2| |

```
e.exists_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|T |
| 3|F |



#### 3.1.2 Exists for patient on patient frame

This example makes use of a patient-level table named `p` and an event-level table named `e` containing the following data:

| patient|b1 |
| - | - |
| 1| |
| 2| |
| 3| |

| patient|b1 |
| - | - |
| 1| |
| 1| |
| 2| |

```
p.exists_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|T |
| 3|T |



### 3.2 Counting the rows for each patient


#### 3.2.1 Count for patient on event frame

This example makes use of a patient-level table named `p` and an event-level table named `e` containing the following data:

| patient|b1 |
| - | - |
| 1| |
| 2| |
| 3| |

| patient|b1 |
| - | - |
| 1| |
| 1| |
| 2| |

```
e.count_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|2 |
| 2|1 |
| 3|0 |



#### 3.2.2 Count for patient on patient frame

This example makes use of a patient-level table named `p` and an event-level table named `e` containing the following data:

| patient|b1 |
| - | - |
| 1| |
| 2| |
| 3| |

| patient|b1 |
| - | - |
| 1| |
| 1| |
| 2| |

```
p.count_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|1 |
| 2|1 |
| 3|1 |



## 4 Aggregating event series


### 4.1 Minimum and maximum aggregations


#### 4.1.1 Minimum for patient

This example makes use of an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 1|102 |
| 1|103 |
| 2|201 |
| 2| |
| 3| |

```
e.i1.minimum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|101 |
| 2|201 |
| 3| |



#### 4.1.2 Maximum for patient

This example makes use of an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 1|102 |
| 1|103 |
| 2|201 |
| 2| |
| 3| |

```
e.i1.maximum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|103 |
| 2|201 |
| 3| |



### 4.2 Sum aggregation


#### 4.2.1 Sum for patient

This example makes use of an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 1|102 |
| 1|103 |
| 2|201 |
| 2| |
| 2|203 |
| 3| |

```
e.i1.sum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|306 |
| 2|404 |
| 3| |



### 4.3 Mean aggregation


#### 4.3.1 Mean for patient integer

This example makes use of an event-level table named `e` containing the following data:

| patient|i1|f1 |
| - | - | - |
| 1|1|1.1 |
| 1|2|2.1 |
| 1|3|3.1 |
| 2|| |
| 2|2|2.1 |
| 2|3|3.1 |
| 3|| |

```
e.i1.mean_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|2.0 |
| 2|2.5 |
| 3| |



#### 4.3.2 Mean for patient float

This example makes use of an event-level table named `e` containing the following data:

| patient|i1|f1 |
| - | - | - |
| 1|1|1.1 |
| 1|2|2.1 |
| 1|3|3.1 |
| 2|| |
| 2|2|2.1 |
| 2|3|3.1 |
| 3|| |

```
e.f1.mean_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|2.1 |
| 2|2.6 |
| 3| |



## 5 Combining series


### 5.1 Combining two patient series


#### 5.1.1 Patient series and patient series

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|102 |
| 2|201|202 |

```
p.i1 + p.i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|203 |
| 2|403 |



### 5.2 Combining a patient series with a value


#### 5.2.1 Patient series and value

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 2|201 |

```
p.i1 + 1
```
returns the following patient series:

| patient | value |
| - | - |
| 1|102 |
| 2|202 |



#### 5.2.2 Value and patient series

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 2|201 |

```
1 + p.i1
```
returns the following patient series:

| patient | value |
| - | - |
| 1|102 |
| 2|202 |



### 5.3 Combining two event series


#### 5.3.1 Event series and event series

This example makes use of an event-level table named `e` containing the following data:

| patient|i1|i2|s1 |
| - | - | - | - |
| 1|101|111|b |
| 1|102|112|a |
| 2|201|211|b |
| 2|202|212|a |

```
(e.i1 + e.i2).sum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|426 |
| 2|826 |



#### 5.3.2 Event series and sorted event series
The sort order of the underlying event series does not affect their combination.

This example makes use of an event-level table named `e` containing the following data:

| patient|i1|i2|s1 |
| - | - | - | - |
| 1|101|111|b |
| 1|102|112|a |
| 2|201|211|b |
| 2|202|212|a |

```
(e.i1 + e.sort_by(e.s1).i2).minimum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|212 |
| 2|412 |



### 5.4 Combining an event series with a patient series


#### 5.4.1 Event series and patient series

This example makes use of a patient-level table named `p` and an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 2|201 |

| patient|i1 |
| - | - |
| 1|111 |
| 1|112 |
| 2|211 |
| 2|212 |

```
(e.i1 + p.i1).sum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|425 |
| 2|825 |



#### 5.4.2 Patient series and event series

This example makes use of a patient-level table named `p` and an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 2|201 |

| patient|i1 |
| - | - |
| 1|111 |
| 1|112 |
| 2|211 |
| 2|212 |

```
(p.i1 + e.i1).sum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|425 |
| 2|825 |



### 5.5 Combining an event series with a value


#### 5.5.1 Event series and value

This example makes use of an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 1|102 |
| 2|201 |
| 2|202 |

```
(e.i1 + 1).sum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|205 |
| 2|405 |



#### 5.5.2 Value and event series

This example makes use of an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 1|102 |
| 2|201 |
| 2|202 |

```
(1 + e.i1).sum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|205 |
| 2|405 |



## 6 Operations on all series


### 6.1 Testing for equality


#### 6.1.1 Equals

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|101 |
| 2|201|202 |
| 3|301| |
| 4|| |

```
p.i1 == p.i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|F |
| 3| |
| 4| |



#### 6.1.2 Not equals

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|101 |
| 2|201|202 |
| 3|301| |
| 4|| |

```
p.i1 != p.i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|T |
| 3| |
| 4| |



#### 6.1.3 Is null

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|101 |
| 2|201|202 |
| 3|301| |
| 4|| |

```
p.i1.is_null()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|F |
| 3|F |
| 4|T |



#### 6.1.4 Is not null

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|101 |
| 2|201|202 |
| 3|301| |
| 4|| |

```
p.i1.is_not_null()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|T |
| 3|T |
| 4|F |



### 6.2 Testing for containment


#### 6.2.1 Is in

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 2|201 |
| 3|301 |
| 4| |

```
p.i1.is_in([101, 301])
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|F |
| 3|T |
| 4| |



#### 6.2.2 Is not in

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 2|201 |
| 3|301 |
| 4| |

```
p.i1.is_not_in([101, 301])
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|T |
| 3|F |
| 4| |



### 6.3 Map from one set of values to another


#### 6.3.1 Map values

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 2|201 |
| 3|301 |
| 4| |

```
p.i1.map_values({101: "a", 201: "b", 301: "a"}, default="c")
```
returns the following patient series:

| patient | value |
| - | - |
| 1|a |
| 2|b |
| 3|a |
| 4|c |



### 6.4 Replace missing values


#### 6.4.1 If null then integer column

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 2|201 |
| 3|301 |
| 4| |

```
p.i1.if_null_then(0)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|101 |
| 2|201 |
| 3|301 |
| 4|0 |



#### 6.4.2 If null then boolean column

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|101 |
| 2|201 |
| 3|301 |
| 4| |

```
p.i1.is_in([101, 201]).if_null_then(False)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|T |
| 3|F |
| 4|F |



## 7 Operations on boolean series


### 7.1 Logical operations


#### 7.1.1 Not

This example makes use of a patient-level table named `p` containing the following data:

| patient|b1 |
| - | - |
| 1|T |
| 2| |
| 3|F |

```
~p.b1
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2| |
| 3|T |



#### 7.1.2 And

This example makes use of a patient-level table named `p` containing the following data:

| patient|b1|b2 |
| - | - | - |
| 1|T|T |
| 2|T| |
| 3|T|F |
| 4||T |
| 5|| |
| 6||F |
| 7|F|T |
| 8|F| |
| 9|F|F |

```
p.b1 & p.b2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2| |
| 3|F |
| 4| |
| 5| |
| 6|F |
| 7|F |
| 8|F |
| 9|F |



#### 7.1.3 Or

This example makes use of a patient-level table named `p` containing the following data:

| patient|b1|b2 |
| - | - | - |
| 1|T|T |
| 2|T| |
| 3|T|F |
| 4||T |
| 5|| |
| 6||F |
| 7|F|T |
| 8|F| |
| 9|F|F |

```
p.b1 | p.b2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|T |
| 3|T |
| 4|T |
| 5| |
| 6| |
| 7|T |
| 8| |
| 9|F |



## 8 Operations on integer series


### 8.1 Arithmetic operations


#### 8.1.1 Negate

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|111 |
| 2|201| |

```
-p.i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|-111 |
| 2| |



#### 8.1.2 Add

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|111 |
| 2|201| |

```
p.i1 + p.i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|212 |
| 2| |



#### 8.1.3 Subtract

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|111 |
| 2|201| |

```
p.i1 - p.i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|-10 |
| 2| |



#### 8.1.4 Multiply

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|111 |
| 2|201| |

```
p.i1 * p.i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|11211 |
| 2| |



#### 8.1.5 Multiply with constant

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|111 |
| 2|201| |

```
10 * p.i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|1110 |
| 2| |



### 8.2 Comparison operations


#### 8.2.1 Less than

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|201 |
| 2|201|201 |
| 3|301|201 |
| 4||201 |

```
p.i1 < p.i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|F |
| 3|F |
| 4| |



#### 8.2.2 Less than or equal to

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|201 |
| 2|201|201 |
| 3|301|201 |
| 4||201 |

```
p.i1 <= p.i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|T |
| 3|F |
| 4| |



#### 8.2.3 Greater than

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|201 |
| 2|201|201 |
| 3|301|201 |
| 4||201 |

```
p.i1 > p.i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|F |
| 3|T |
| 4| |



#### 8.2.4 Greater than or equal to

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|i2 |
| - | - | - |
| 1|101|201 |
| 2|201|201 |
| 3|301|201 |
| 4||201 |

```
p.i1 >= p.i2
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|T |
| 3|T |
| 4| |



## 9 Operations on all series containing codes


### 9.1 Testing for containment using codes


#### 9.1.1 Is in

This example makes use of a patient-level table named `p` containing the following data:

| patient|c1 |
| - | - |
| 1|abc |
| 2|def |
| 3|ghi |
| 4| |

```
p.c1.is_in([SNOMEDCTCode("abc"), SNOMEDCTCode("ghi")])
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|F |
| 3|T |
| 4| |



#### 9.1.2 Is not in

This example makes use of a patient-level table named `p` containing the following data:

| patient|c1 |
| - | - |
| 1|abc |
| 2|def |
| 3|ghi |
| 4| |

```
p.c1.is_not_in([SNOMEDCTCode("abc"), SNOMEDCTCode("ghi")])
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|T |
| 3|F |
| 4| |



#### 9.1.3 Is in codelist csv

This example makes use of a patient-level table named `p` containing the following data:

| patient|c1 |
| - | - |
| 1|abc |
| 2|def |
| 3|ghi |
| 4| |

```
p.c1.is_in(codelist)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|F |
| 3|T |
| 4| |



### 9.2 Test mapping codes to categories using a categorised codelist


#### 9.2.1 Map codes to categories

This example makes use of a patient-level table named `p` containing the following data:

| patient|c1 |
| - | - |
| 1|abc |
| 2|def |
| 3|ghi |
| 4| |

```
p.c1.to_category(codelist.my_categorisation)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|cat1 |
| 2| |
| 3|cat2 |
| 4| |



## 10 Logical case expressions


### 10.1 Logical case expressions


#### 10.1.1 Case with expression

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|6 |
| 2|7 |
| 3|8 |
| 4|9 |
| 5| |

```
case(
    when(p.i1 < 8).then(p.i1),
    when(p.i1 > 8).then(100),
)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|6 |
| 2|7 |
| 3| |
| 4|100 |
| 5| |



#### 10.1.2 Case with default

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|6 |
| 2|7 |
| 3|8 |
| 4|9 |
| 5| |

```
case(
    when(p.i1 < 8).then(p.i1),
    when(p.i1 > 8).then(100),
    default=0,
)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|6 |
| 2|7 |
| 3|0 |
| 4|100 |
| 5|0 |



#### 10.1.3 Case with boolean column

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1|b1 |
| - | - | - |
| 1|6|T |
| 2|7|F |
| 3|9|F |
| 4| |

```
case(
    when(p.b1).then(p.i1),
    when(p.i1 > 8).then(100),
)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|6 |
| 2| |
| 3|100 |
| 4| |



## 11 Operations on all series containing dates


### 11.1 Operations which apply to all series containing dates


#### 11.1.1 Get year

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1|i1 |
| - | - | - |
| 1|1990-01-02|100 |
| 2|2000-03-04|200 |
| 3|| |

```
p.d1.year
```
returns the following patient series:

| patient | value |
| - | - |
| 1|1990 |
| 2|2000 |
| 3| |



#### 11.1.2 Get month

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1|i1 |
| - | - | - |
| 1|1990-01-02|100 |
| 2|2000-03-04|200 |
| 3|| |

```
p.d1.month
```
returns the following patient series:

| patient | value |
| - | - |
| 1|1 |
| 2|3 |
| 3| |



#### 11.1.3 Get day

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1|i1 |
| - | - | - |
| 1|1990-01-02|100 |
| 2|2000-03-04|200 |
| 3|| |

```
p.d1.day
```
returns the following patient series:

| patient | value |
| - | - |
| 1|2 |
| 2|4 |
| 3| |



#### 11.1.4 To first of year

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|1990-01-01 |
| 2|2000-12-15 |
| 3|2020-12-31 |
| 4| |

```
p.d1.to_first_of_year()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|1990-01-01 |
| 2|2000-01-01 |
| 3|2020-01-01 |
| 4| |



#### 11.1.5 To first of month

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|1990-01-01 |
| 2|1990-01-31 |
| 3| |

```
p.d1.to_first_of_month()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|1990-01-01 |
| 2|1990-01-01 |
| 3| |



#### 11.1.6 Add days

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1|i1 |
| - | - | - |
| 1|1990-01-02|100 |
| 2|2000-03-04|200 |
| 3|| |

```
p.d1 + days(p.i1)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|1990-04-12 |
| 2|2000-09-20 |
| 3| |



#### 11.1.7 Subtract days

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1|i1 |
| - | - | - |
| 1|1990-01-02|100 |
| 2|2000-03-04|200 |
| 3|| |

```
p.d1 - days(p.i1)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|1989-09-24 |
| 2|1999-08-17 |
| 3| |



#### 11.1.8 Add months

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1|i1 |
| - | - | - |
| 1|2003-01-29|1 |
| 2|2004-01-29|1 |
| 3|2003-01-31|1 |
| 4|2004-01-31|1 |
| 5|2004-03-31|-1 |
| 6|2000-10-31|11 |
| 7|2000-10-31|-11 |

```
p.d1 + months(p.i1)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|2003-03-01 |
| 2|2004-02-29 |
| 3|2003-03-01 |
| 4|2004-03-01 |
| 5|2004-03-01 |
| 6|2001-10-01 |
| 7|1999-12-01 |



#### 11.1.9 Add years

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1|i1 |
| - | - | - |
| 1|2000-06-15|5 |
| 2|2000-06-15|-5 |
| 3|2004-02-29|1 |
| 4|2004-02-29|-1 |
| 5|2004-02-29|4 |
| 6|2004-02-29|-4 |
| 7|2003-03-01|1 |

```
p.d1 + years(p.i1)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|2005-06-15 |
| 2|1995-06-15 |
| 3|2005-03-01 |
| 4|2003-03-01 |
| 5|2008-02-29 |
| 6|2000-02-29 |
| 7|2004-03-01 |



#### 11.1.10 Add date to duration

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1|i1 |
| - | - | - |
| 1|1990-01-02|100 |
| 2|2000-03-04|200 |
| 3|| |

```
days(100) + p.d1
```
returns the following patient series:

| patient | value |
| - | - |
| 1|1990-04-12 |
| 2|2000-06-12 |
| 3| |



#### 11.1.11 Difference between dates in years

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|2020-02-29 |
| 2|2020-02-28 |
| 3|2019-01-01 |
| 4|2021-03-01 |
| 5|2023-01-01 |
| 6| |

```
(date(2021, 2, 28) - p.d1).years
```
returns the following patient series:

| patient | value |
| - | - |
| 1|0 |
| 2|1 |
| 3|2 |
| 4|-1 |
| 5|-2 |
| 6| |



#### 11.1.12 Difference between dates in months

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1|d2 |
| - | - | - |
| 1|2000-02-28|2000-01-30 |
| 2|2000-03-01|2000-01-30 |
| 3|2000-03-28|2000-02-28 |
| 4|2000-03-30|2000-01-30 |
| 5|2000-02-27|2000-01-30 |
| 6|2000-01-27|2000-01-30 |
| 7|1999-12-26|2000-01-27 |
| 8|2005-02-28|2004-02-29 |
| 9|2010-01-01|2000-01-01 |
| 10|2000-01-01| |

```
(p.d1 - p.d2).months
```
returns the following patient series:

| patient | value |
| - | - |
| 1|0 |
| 2|1 |
| 3|1 |
| 4|2 |
| 5|0 |
| 6|-1 |
| 7|-2 |
| 8|11 |
| 9|120 |
| 10| |



#### 11.1.13 Difference between dates in days

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1|d2 |
| - | - | - |
| 1|2000-01-01|2000-01-01 |
| 2|2000-03-01|2000-01-01 |
| 3|2001-03-01|2001-01-01 |
| 4|1999-12-31|2001-01-01 |

```
(p.d1 - p.d2).days
```
returns the following patient series:

| patient | value |
| - | - |
| 1|0 |
| 2|60 |
| 3|59 |
| 4|-367 |



#### 11.1.14 Reversed date differences

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|1990-01-30 |
| 2|1970-01-15 |

```
(p.d1 - "1980-01-20").years
```
returns the following patient series:

| patient | value |
| - | - |
| 1|10 |
| 2|-11 |



#### 11.1.15 Add days to static date

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|10 |
| 2|-10 |

```
date(2000, 1, 1) + days(p.i1)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|2000-01-11 |
| 2|1999-12-22 |



#### 11.1.16 Add months to static date

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|10 |
| 2|-10 |

```
date(2000, 1, 1) + months(p.i1)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|2000-11-01 |
| 2|1999-03-01 |



#### 11.1.17 Add years to static date

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|10 |
| 2|-10 |

```
date(2000, 1, 1) + years(p.i1)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|2010-01-01 |
| 2|1990-01-01 |



### 11.2 Comparisons involving dates


#### 11.2.1 Is before

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|1990-01-01 |
| 2|2000-01-01 |
| 3|2010-01-01 |
| 4| |

```
p.d1.is_before(date(2000, 1, 1))
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|F |
| 3|F |
| 4| |



#### 11.2.2 Is on or before

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|1990-01-01 |
| 2|2000-01-01 |
| 3|2010-01-01 |
| 4| |

```
p.d1.is_on_or_before(date(2000, 1, 1))
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|T |
| 3|F |
| 4| |



#### 11.2.3 Is after

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|1990-01-01 |
| 2|2000-01-01 |
| 3|2010-01-01 |
| 4| |

```
p.d1.is_after(date(2000, 1, 1))
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|F |
| 3|T |
| 4| |



#### 11.2.4 Is on or after

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|1990-01-01 |
| 2|2000-01-01 |
| 3|2010-01-01 |
| 4| |

```
p.d1.is_on_or_after(date(2000, 1, 1))
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|T |
| 3|T |
| 4| |



#### 11.2.5 Is in

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|1990-01-01 |
| 2|2000-01-01 |
| 3|2010-01-01 |
| 4| |

```
p.d1.is_in([date(2010, 1, 1), date(1900, 1, 1)])
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|F |
| 3|T |
| 4| |



#### 11.2.6 Is not in

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|1990-01-01 |
| 2|2000-01-01 |
| 3|2010-01-01 |
| 4| |

```
p.d1.is_not_in([date(2010, 1, 1), date(1900, 1, 1)])
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|T |
| 3|F |
| 4| |



#### 11.2.7 Is between

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|2010-01-01 |
| 2|2010-01-02 |
| 3|2010-01-03 |
| 4|2010-01-04 |
| 5|2010-01-05 |
| 6| |

```
p.d1.is_between(date(2010, 1, 2), date(2010, 1, 4))
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|F |
| 3|T |
| 4|F |
| 5|F |
| 6| |



#### 11.2.8 Is on or between

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|2010-01-01 |
| 2|2010-01-02 |
| 3|2010-01-03 |
| 4|2010-01-04 |
| 5|2010-01-05 |
| 6| |

```
p.d1.is_on_or_between(date(2010, 1, 2), date(2010, 1, 4))
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|T |
| 3|T |
| 4|T |
| 5|F |
| 6| |



#### 11.2.9 Is between backwards

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|2010-01-01 |
| 2|2010-01-02 |
| 3|2010-01-03 |
| 4|2010-01-04 |
| 5|2010-01-05 |
| 6| |

```
p.d1.is_between(date(2010, 1, 4), date(2010, 1, 2))
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|F |
| 3|F |
| 4|F |
| 5|F |
| 6| |



#### 11.2.10 Is on or between backwards

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1 |
| - | - |
| 1|2010-01-01 |
| 2|2010-01-02 |
| 3|2010-01-03 |
| 4|2010-01-04 |
| 5|2010-01-05 |
| 6| |

```
p.d1.is_on_or_between(date(2010, 1, 4), date(2010, 1, 2))
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|F |
| 3|F |
| 4|F |
| 5|F |
| 6| |



### 11.3 Types usable in comparisons involving dates


#### 11.3.1 Accepts python date object

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1|d2 |
| - | - | - |
| 1|1990-01-01|1980-01-01 |
| 2|2000-01-01|1980-01-01 |
| 3|2010-01-01|2020-01-01 |
| 4||2020-01-01 |

```
p.d1.is_before(datetime.date(2000, 1, 20))
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|T |
| 3|F |
| 4| |



#### 11.3.2 Accepts iso formated date string

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1|d2 |
| - | - | - |
| 1|1990-01-01|1980-01-01 |
| 2|2000-01-01|1980-01-01 |
| 3|2010-01-01|2020-01-01 |
| 4||2020-01-01 |

```
p.d1.is_before("2000-01-20")
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|T |
| 3|F |
| 4| |



#### 11.3.3 Accepts another date series

This example makes use of a patient-level table named `p` containing the following data:

| patient|d1|d2 |
| - | - | - |
| 1|1990-01-01|1980-01-01 |
| 2|2000-01-01|1980-01-01 |
| 3|2010-01-01|2020-01-01 |
| 4||2020-01-01 |

```
p.d1.is_before(p.d2)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|F |
| 2|F |
| 3|T |
| 4| |



## 12 Operations on all series containing strings


### 12.1 Testing whether one string contains another string


#### 12.1.1 Contains fixed value

This example makes use of a patient-level table named `p` containing the following data:

| patient|s1 |
| - | - |
| 1|ab |
| 2|ab12 |
| 3|12ab |
| 4|12ab45 |
| 5|a b |
| 6|AB |
| 7| |

```
p.s1.contains("ab")
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|T |
| 3|T |
| 4|T |
| 5|F |
| 6|F |
| 7| |



#### 12.1.2 Contains fixed value with special characters

This example makes use of a patient-level table named `p` containing the following data:

| patient|s1 |
| - | - |
| 1|/a%b_ |
| 2|/ab_ |
| 3|/a%bc |
| 4|a%b_ |

```
p.s1.contains("/a%b_")
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|F |
| 3|F |
| 4|F |



#### 12.1.3 Contains value from column

This example makes use of a patient-level table named `p` containing the following data:

| patient|s1|s2 |
| - | - | - |
| 1|ab|ab |
| 2|cd12|cd |
| 3|12ef|ef |
| 4|12gh45|gh |
| 5|i j|ij |
| 6|KL|kl |
| 7||mn |
| 8|ab| |

```
p.s1.contains(p.s2)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|T |
| 3|T |
| 4|T |
| 5|F |
| 6|F |
| 7| |
| 8| |



#### 12.1.4 Contains value from column with special characters

This example makes use of a patient-level table named `p` containing the following data:

| patient|s1|s2 |
| - | - | - |
| 1|/a%b_|/a%b_ |
| 2|/ab_|/a%b_ |
| 3|/a%bc|/a%b_ |
| 4|a%b_|/a%b_ |

```
p.s1.contains(p.s2)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|F |
| 3|F |
| 4|F |



## 13 Defining the dataset population


### 13.1 Defining a population

`set_population` is used to limit the population from which data is extracted.



#### 13.1.1 Population with single table
Extract a column from a patient table after limiting the population by another column.

This example makes use of a patient-level table named `p` containing the following data:

| patient|b1|i1 |
| - | - | - |
| 1|F|10 |
| 2|T|20 |
| 3|F|30 |

```
p.i1
set_population(~p.b1)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|10 |
| 3|30 |



#### 13.1.2 Population with multiple tables
Limit the patient population by a column in one table, and return values from another
table.

This example makes use of a patient-level table named `p` and an event-level table named `e` containing the following data:

| patient|i1 |
| - | - |
| 1|10 |
| 2|20 |
| 3|0 |

| patient|i1 |
| - | - |
| 1|101 |
| 1|102 |
| 3|301 |
| 4|401 |

```
e.exists_for_patient()
set_population(p.i1 > 0)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|T |
| 2|F |



#### 13.1.3 Case with case expression
Limit the patient population by a case expression.

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|6 |
| 2|7 |
| 3|9 |
| 4| |

```
p.i1
set_population(
    case(
        when(p.i1 <= 8).then(True),
        when(p.i1 > 8).then(False),
    )
)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|6 |
| 2|7 |



## 14 Defining a table using inline data


### 14.1 Defining a table using inline data


#### 14.1.1 Table from rows

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|10 |
| 2|20 |
| 3|30 |

```
p.i1 + t.n
```
returns the following patient series:

| patient | value |
| - | - |
| 1|110 |
| 2| |
| 3|330 |