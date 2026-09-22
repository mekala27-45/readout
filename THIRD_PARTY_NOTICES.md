# Third-party notices

Readout is distributed under the Apache License, Version 2.0, reproduced in [LICENSE](LICENSE). The source material listed below retains its upstream copyright and license notices. This file covers directly reused source material; installed dependencies retain their own distribution licenses.

## cityflow

- Revision: `2163b362d75458e8485f3f78fdec85b7322e6fd7`.
- Source: [pinned upstream license](https://github.com/mekala27-45/cityflow/blob/2163b362d75458e8485f3f78fdec85b7322e6fd7/LICENSE).
- License: Apache-2.0.
- Copyright: 2026 Ajay Mekala.
- Reused material: the Benjamini-Hochberg implementation in `packages/stats/src/readout_stats/cityflow_fdr.py`, the palette validator in `scripts/palette_core.cjs`, and the document-rendering approach adapted for the claim gate. [Port provenance](docs/port-provenance.md) identifies the source files and adaptations.

The pinned upstream license file contains the following notice. The full Apache License, Version 2.0 is included in this distribution's [LICENSE](LICENSE).

```text
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   Copyright 2026 Ajay Mekala
```

## trajectory

- Revision: `51a8b62ef483623baed2b7b8eab744b636d3d576`.
- Source: [pinned upstream license](https://github.com/mekala27-45/trajectory/blob/51a8b62ef483623baed2b7b8eab744b636d3d576/LICENSE).
- License: Apache-2.0. The upstream file contains the complete Apache License, Version 2.0, including the copyright notice below. The complete license is retained in this distribution's [LICENSE](LICENSE).
- Copyright: 2026 Ajay Mekala.
- Reused material: StrictModel contract behavior in `packages/core/src/readout_core/models.py`, adapted with additional strict typing, finite-value checks, and experiment-specific validation.

```text
   Copyright 2026 Ajay Mekala

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```

## pricepoint

- Revision: `e1a1db84249c562f895de23d5ec6627675ee1147`.
- Source: [pinned upstream license](https://github.com/mekala27-45/pricepoint/blob/e1a1db84249c562f895de23d5ec6627675ee1147/LICENSE).
- License: MIT.
- Copyright: (c) 2026 Ajay Mekala.
- Reused material: the assumptions, planning calculation, elasticity discussion, and results retained under `experiments/pricepoint`, and inherited build-tooling adaptations. These upstream materials retain the MIT notice reproduced below.

```text
MIT License

Copyright (c) 2026 Ajay Mekala

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

No root `NOTICE` file was present at any of the three pinned upstream revisions when their notices were checked. The public dataset has separate provenance and terms in [experiments/cookie_cats/PROVENANCE.md](experiments/cookie_cats/PROVENANCE.md).
