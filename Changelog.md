## Changelog file for pyproperties

### Most recent version can be found on [GitHub]()
### _Packages_ can be downloaded from [SourceForge](https://sourceforge.net/projects/pyproperties/)

* Contact: [Twitter](http://twitter.com/triviuss), [GitHub](https://github.com/marekjm), [SF]([SourceForge](https://sourceforge.net/projects/pyproperties/))

&nbsp;

> ### "Part of being a good steward to a successful project is realizing that writing code for yourself is a Bad Idea™. If thousands of people are using your code, then write your code for maximum clarity, not your personal preference of how to get clever within the spec."
>_Idan_ _Gazit_


## Table of Contents

 * [Whitespace](#whitespace)



------------------------------------------------


1. <a name="whitespace">Whitespace</a>
  - Never mix spaces and tabs.
  - When beginning a project, before you write any code, choose between soft indents (spaces) or real tabs, consider this **law**.
      - For readability, I always recommend setting your editor's indent size to two characters &mdash; this means two spaces or two spaces representing a real tab.
  - If your editor supports it, always work with the "show invisibles" setting turned on. The benefits of this practice are:
      - Enforced consistency
      - Eliminating end of line whitespace
      - Eliminating blank line whitespace
      - Commits and diffs that are easier to read


    ```javascript

    // if/else/for/while/try always have spaces, braces and span multiple lines
    // this encourages readability

    // 2.A.1.1
    // Examples of really cramped syntax

    if(condition) doSomething();

    while(condition) iterating++;

    for(var i=0;i<100;i++) someIterativeFn();
    ```