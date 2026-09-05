<!--
------------------( LICENSE                                  )------------------
Copyright (c) 2014-2026 Beartype authors.
See "LICENSE" for further details.

------------------( SYNOPSIS                                 )------------------
Child Markdown document detailing installation instructions.
-->

# Install

Install beartype with [pip], because [PyPI][beartype PyPI] is the [cheese shop][PyPI] and you too enjoy a [fine Venezuelan beaver cheese][cheese shop sketch] while mashing disconsolately on your keyboard late on a rain-soaked Friday evening. Wherever expensive milk byproducts ferment, beartype will be there.

```bash
pip3 install beartype
```

Install beartype with [Anaconda], because package managers named after vicious South American murder reptiles have finally inspired your team to embrace more mammal-friendly packages. Your horoscope also reads: "Avoid reckless ecotourism in places that rain alot."

```bash
conda config --add channels conda-forge
conda install beartype
```

[Commemorate this moment in time](#badge) with [![bear-ified](https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg)](https://beartype.readthedocs.io), our over*bear*ing project shield. What says quality like [a bear on a badge](#badge), amirite?

## Platform

Beartype is also installable with platform-specific package managers, because sometimes you just need this thing to work.

### macOS

Let's install beartype with [Homebrew][HomeBrew] on [macOS] courtesy [our third-party tap][beartype Homebrew]:

```bash
brew install beartype/beartype/beartype
```

Let's install beartype with [MacPorts] on [macOS]:

```bash
sudo port install py-beartype
```

A big bear hug to [our official macOS package maintainer @harens][harens] for [packaging beartype for our Apple-appreciating audience][beartype MacPorts].

### Arch Linux

Let's install beartype with `pacman` on [Arch Linux] – where beartype is now [officially packaged][beartype Arch] in the [Arch User Repository (AUR)][beartype Arch] itself:

```bash
git clone https://aur.archlinux.org/python-beartype.git
cd python-beartype
makepkg -si
```

Truly, Arch Linux has now seen the face of quality assurance. It looks like a grizzled bear with patchy fur, one twitchy eye, and a gimpy leg that spasmodically flails around.

### Gentoo Linux

Let's install beartype with `emerge` on [Gentoo Linux] – where beartype is now [officially packaged][beartype Gentoo] in the Portage tree itself:

```bash
emerge beartype
```

Source-based Linux distributions are the CPU-bound nuclear option. *What could be simpler?* O_o

## Badge

If you're feeling the quality assurance and want to celebrate, consider signaling that you're now publicly *bear-*ified:

> YummySoft is now [![bear-ified](https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg)](https://beartype.readthedocs.io)!

All this magic and possibly more can be yours with:

- **Markdown**:

  ```md
  YummySoft is now [![bear-ified](https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg)](https://beartype.readthedocs.io)!
  ```

- **reStructuredText**:

  ```rst
  YummySoft is now |bear-ified|!

  .. # See https://docutils.sourceforge.io/docs/ref/rst/directives.html#image
  .. |bear-ified| image:: https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg
     :align: top
     :target: https://beartype.readthedocs.io
     :alt: bear-ified
  ```

- **Raw HTML**:

  ```html
  YummySoft is now <a href="https://beartype.readthedocs.io"><img
    src="https://raw.githubusercontent.com/beartype/beartype-assets/main/badge/bear-ified.svg"
    alt="bear-ified"
    style="vertical-align: middle;"></a>!
  ```

Let a soothing pastel bear give your users the reassuring **OK** sign.
