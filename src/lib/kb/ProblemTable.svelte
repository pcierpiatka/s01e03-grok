<script lang="ts">
  import counts from '#lib/data/problem-counts.json';
</script>

<table>
  <thead>
    <tr><th>problem</th><th>reports</th><th>where the desk's view shows it</th></tr>
  </thead>
  <tbody>
    {#each counts.problems as problem (problem.id)}
      <tr>
        <td><code>{problem.id}</code></td>
        <td>{problem.reports}</td>
        <td>{problem.where}</td>
      </tr>
    {/each}
  </tbody>
</table>

{#each counts.problems as problem (problem.id)}
  <p><code>{problem.id}</code> — {problem.note}</p>
{/each}
