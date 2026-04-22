# Guide for database.py

[quick link to database.py](../src/database.py)

## 1. public methods

<table>
<thread>
 <tr>
  <th>method name</th>
  <th>feature</th>
  <th>input</th>
  <th>output</th>
 </tr>
</thread>
<tr>
 <td>close()</td>
 <td>close both the database and the temporary data</td>
 <td></td>
 <td>True / False</td>
</tr>
<tr>
 <td>isRegistered()</td>
 <td></td>
 <td>player ID</td>
 <td>codename / False</td>
</tr>
<tr>
 <td>findNewPlayerID()</td>
 <td>yields one player ID unused</td>
 <td></td>
 <td>player ID (not confirmed)</td>
</tr>
<tr>
 <td>usePlayerID()</td>
 <td>add new player info to the permanent database; succeeds iff the input ID is yet to be registered to the database</td>
 <td>player ID, codename</td>
 <td>True / False</td>
</tr>
<tr>
 <td>addPlayerNextGame()</td>
 <td>succeeds iff the player ID is registered to the database</td>
 <td>player ID, team ID, equipment ID</td>
 <td>True / False</td>
</tr>
<tr>
 <td>showTable()</td>
 <td>debug: prints a full list of player infor registered to the database table on the CLI</td>
 <td></td>
 <td>True / False</td>
</tr>

</table>

## 2. Database structure
1. player ID (primary key) - codename - highest score - # of games played

## 3. Temporary data available in-game
1. player ID - current score - team ID
2. equipment ID - player ID
