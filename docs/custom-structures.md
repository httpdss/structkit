# Creating Custom Structures

Let's say you are happy with the default structures that StructKit provides, but you want to customize them for your specific needs. This is totally possible!

The best way to approach this is to have a repository where you can store your custom structures. You can then reference these structures in your `.struct.yaml` files.

## Suggested Repository Structure

Here is a suggested structure for your custom structures repository:

```sh
structures/
├── category1/
│   ├── structure1.yaml
│   └── structure2.yaml
├── category2/
│   ├── structure1.yaml
│   └── structure2.yaml
```

This way you could reference your custom structures in your `.struct.yaml` files like this:

```yaml
folders:
  - ./:
    struct:
      - category1/structure1
      - category2/structure2
    with:
      var_in_structure1: 'value'
```

For this to work, you will need to set the path to the custom structures repository using the `-s` option when running StructKit:

```sh
structkit generate -s ~/path/to/custom-structures/structures file://.struct.yaml ./output
```
