# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the GNU Affero General Public License version 3.
# See LICENSE or go to <https://www.gnu.org/licenses/agpl-3.0.txt> for full license details.

from pyro_risks.train import main, parse_args
import sys

if __name__ == "__main__":

    args = parse_args(sys.argv[1:])
    main(args)
