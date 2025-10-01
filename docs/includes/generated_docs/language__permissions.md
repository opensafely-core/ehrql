
<h4 class="attr-heading" id="claim_permissions" data-toc-label="claim_permissions" markdown>
  <tt><strong>claim_permissions</strong>(<em>*permissions</em>)</tt>
</h4>
<div markdown="block" class="indent">
This function allows you to access any restricted table or feature when working with
dummy data. It will NOT allow you access with real data: for that you will need the
appropriate permissions on the OpenSAFELY platform.

Permission names are strings and should be written with double quotes e.g.

    from ehrql import claim_permissions

    claim_permissions("some_permission", "another_permission")

This can go anywhere in your dataset or measure definition file.

You can make multiple `claim_permissions()` calls and the permissions will be
combined together.
</div>
