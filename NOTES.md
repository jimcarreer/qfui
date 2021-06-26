# General Approach

* Loading of CSV Done
** Re-implement code from plugin / lua
* Get Display Done
** Blueprint navigation tree
** Layer viewer
* Get editing done

Basic layout desired:

    |------------------------------|
    |------------------------------|
    |                     |        |
    |                     |        |
    |                     |        |
    |    Layer Viewer     | BPTree |
    |                     |        |
    |                     |        |
    |                     |        |
    |------------------------------|

Floating windows for "tools" like GIMP and other complex UIs.

# Questions

* How do I make a GraphicsView scrollable / resizable to the parent widget?
* Layouts in QT in general (Grid / Column based?)

# QF Data Structure

It looks as though data from blueprints loads as the user requests it to, not
at startup of DF or when QF runs, so I should mirror that approach.

Parsing code:
https://github.com/DFHack/scripts/blob/13fbb5a84d59d43bf68ce190726192484d52e00a/internal/quickfort/parse.lua

Test Case:
https://github.com/DFHack/dfhack/blob/develop/data/blueprints/library/dreamfort.csv

* This has 84 Sections as far as I can tell from the qf gui
* This has 11? Dig Sections
* This has 24? Build Sections
* This has 6? Place Sections
* This has 2? Zone Sections
* This has 14? Query Sections
* This has 20? Meta Sections
* This has 8? Note Sections
* This has 1? Ignore Sections

This makes 86 but ignore sections are not visible, but I cannot account for the missing section.


Blueprint Properties
* Has 1 or more files
* Files can be nested in directories
* Directory names should probably be flattened in Tree View

File properties
* Has 1 or more sections

SectionRexer properties
* Has 1 label
* Has 1 mode
* Has metadata?
* Has 1 or more Layers
* Layer dimensions independent?
* Layer start location independent? 

Layer properties
* Metadata?
* Dimensions?
* Start?
* Grid

# Parser Context

The QFParser module should use a logger and log adapter to trace issues
with the file being parsed as debugs/infos/errors/warns. Specifically 
line no / cell position / char position will be important.  This should just
be extra log context updated whenever appropriate, possibly at the start of 
for loops that iterate lines and reset at the end of the relevant loop
https://docs.python.org/3/howto/logging-cookbook.html#adding-contextual-information-to-your-logging-output

# DF Hack and Lua Notes
https://github.com/DFHack/dfhack/blob/develop/library/lua/utils.lua
* utils.invert takes a list and creates a dictionary:


    {
        "first_element": 0,
        "second_element": 1
    }

Dump function for lua, put in qf common:
    
    function dumper (tbl, indent)
      if not indent then indent = 0 end
      for k, v in pairs(tbl) do
        formatting = string.rep("  ", indent) .. k .. ": "
        if type(v) == "table" then
          print(formatting)
          dumper(v, indent+1)
        elseif type(v) == 'boolean' then
          print(formatting .. tostring(v))
        else
          print(formatting .. v)
        end
      end
    end